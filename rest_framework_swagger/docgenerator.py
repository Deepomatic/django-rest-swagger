"""Generates API documentation by introspection."""
import importlib
import rest_framework
from rest_framework import viewsets
from rest_framework.serializers import Serializer, BaseSerializer
from rest_framework_swagger import SWAGGER_SETTINGS

from .introspectors import (
    APIViewIntrospector,
    BaseMethodIntrospector,
    IntrospectorHelper,
    ViewSetIntrospector,
    WrappedAPIViewIntrospector,
    get_data_type,
    get_default_value,
    get_primitive_type
)
from .compat import OrderedDict

import logging
logger = logging.getLogger(__name__)

class DocumentationGeneratorBase(object):
    def __init__(self, for_user=None):

        # unauthenticated user is expected to be in the form 'module.submodule.Class' if a value is present
        unauthenticated_user = SWAGGER_SETTINGS.get('unauthenticated_user')

        # attempt to load unathenticated_user class from settings if a user is not supplied
        if not for_user and unauthenticated_user:
            module_name, class_name = unauthenticated_user.rsplit(".", 1)
            unauthenticated_user_class = getattr(importlib.import_module(module_name), class_name)
            for_user = unauthenticated_user_class()

        self.user = for_user

        # Serializers defined in docstrings
        self.explicit_serializers = set()

        # Serializers defined in fields
        self.fields_serializers = set()

        # Response classes defined in docstrings
        self.explicit_response_types = dict()


    def get_introspector(self, api, apis):
        path = api['path']
        pattern = api['pattern']
        callback = api['callback']
        if callback.__module__ == 'rest_framework.decorators':
            return WrappedAPIViewIntrospector(callback, path, pattern, self.user)
        elif issubclass(callback, viewsets.ViewSetMixin):
            patterns = [a['pattern'] for a in apis
                        if a['callback'] == callback]
            return ViewSetIntrospector(callback, path, pattern, self.user, patterns=patterns)
        else:
            return APIViewIntrospector(callback, path, pattern, self.user)

    def _get_response_serializer(self, method_inspector):
        """
        Returns serializer used in method.
        Registers custom serializer from docstring in scope.

        Serializer might be ignored if explicitly told in docstring
        """
        doc_parser = method_inspector.get_yaml_parser()

        if doc_parser.get_response_type() is not None:
            # Custom response class detected
            return None

        if doc_parser.should_omit_serializer():
            return None

        serializer = method_inspector.get_response_serializer_class()
        return serializer

    def _get_method_response_type(self, doc_parser, serializer,
                                  view_inspector, method_inspector):
        """
        Returns response type for method.
        This might be custom `type` from docstring or discovered
        serializer class name.

        Once custom `type` found in docstring - it'd be
        registered in a scope
        """
        response_type = doc_parser.get_response_type()
        if response_type is not None:
            # Register class in scope
            view_name = view_inspector.callback.__name__
            view_name = view_name.replace('ViewSet', '')
            view_name = view_name.replace('APIView', '')
            view_name = view_name.replace('View', '')
            response_type_name = "{view}{method}Response".format(
                view=view_name,
                method=method_inspector.method.title().replace('_', '')
            )
            self.explicit_response_types.update({
                response_type_name: {
                    "id": response_type_name,
                    "properties": response_type
                }
            })
            return response_type_name
        else:
            serializer_name = IntrospectorHelper.get_serializer_name(serializer)
            if serializer_name is not None:
                return serializer_name

            return 'object'

    def _get_serializer_set(self, apis):
        """
        Returns a set of serializer classes for a provided list
        of APIs
        """
        serializers = set()

        for api in apis:
            introspector = self.get_introspector(api, apis)
            for method_introspector in introspector:
                serializer = method_introspector.get_request_serializer_class()
                if serializer is not None:
                    serializers.add(serializer)
                serializer = self._get_response_serializer(method_introspector)
                if serializer is not None:
                    serializers.add(serializer)
                extras = method_introspector.get_extra_serializer_classes()
                for extra in extras:
                    if extra is not None:
                        serializers.add(extra)

                parser = method_introspector.get_yaml_parser()
                for response in parser.get_responses(method_introspector.callback):
                    if 'schema' in response and response['schema'] is not None:
                        serializer = parser.load_serializer_class(response['schema'], method_introspector.callback)
                        serializers.add(serializer)

        return serializers

    def _find_field_serializers(self, serializers, found_serializers=set()):
        """
        Returns set of serializers discovered from fields
        """
        def get_thing(field, key):
            if rest_framework.VERSION >= '3.0.0':
                from rest_framework.serializers import ListSerializer, ListField
                if isinstance(field, ListSerializer, ListField):
                    return key(field.child)
            return key(field)

        serializers_set = set()
        for serializer in serializers:
            fields = serializer().get_fields()
            for name, field in fields.items():
                if isinstance(field, BaseSerializer) or isinstance(field, Serializer):
                    serializers_set.add(get_thing(field, lambda f: f))
                    if field not in found_serializers:
                        serializers_set.update(
                            self._find_field_serializers(
                                (get_thing(field, lambda f: f.__class__),),
                                serializers_set))

        return serializers_set

    def _get_serializer_fields(self, serializer):
        """
        Returns serializer fields in the Swagger MODEL format
        """
        if serializer is None:
            return

        if hasattr(serializer, '__call__'):
            fields = serializer().get_fields()
        else:
            fields = serializer.get_fields()

        data = OrderedDict({
            'fields': OrderedDict(),
            'required': [],
            'write_only': [],
            'read_only': [],
        })
        for name, field in fields.items():
            if getattr(field, 'write_only', False):
                data['write_only'].append(name)

            if getattr(field, 'read_only', False):
                data['read_only'].append(name)

            if getattr(field, 'required', True):
                data['required'].append(name)

            f = self._build_serializer_field(field)
            if f is None:
                continue

             # memorize discovered field
            data['fields'][name] = f

        return data

    def _build_serializer_field(self, field):
        f = {}

        description = getattr(field, 'help_text')
        if description == "":
            return None
        if description:
            description = description.strip()
        if description:
            f['description'] = description

        if isinstance(field, BaseSerializer) or isinstance(field, Serializer):
            field_serializer = IntrospectorHelper.get_serializer_name(field)
            if getattr(field, 'write_only', False):
                field_serializer = "Write{}".format(field_serializer)
            f['$ref'] = "#/definitions/%s" % field_serializer
            f['type'] = 'object'
        else:
            data_type, data_format = get_data_type(field) or ('string', 'string')
            if data_type == 'hidden':
                return None
            elif data_type == 'array':
                if isinstance(data_format, BaseSerializer) or isinstance(data_format, Serializer):
                    serializer_name = IntrospectorHelper.get_serializer_name(data_format)
                    items = {
                        '$ref': "#/definitions/%s" % serializer_name
                    }
                else:
                    items = self._build_serializer_field(data_format)
                data_format = data_type
            elif data_type in BaseMethodIntrospector.ENUMS:
                choices = []
                if isinstance(field.choices, list):
                    choices = [k for k, v in field.choices]
                elif isinstance(field.choices, dict):
                    choices = [k for k, v in field.choices.items()]

                if choices:
                    # guest data type and format
                    data_type, data_format = get_primitive_type(choices[0]) or ('string', 'string')
                    f['enum'] = choices

            f['type'] = data_type
            if data_format != f['type']:
                f['format'] = data_format
            default = get_default_value(field)
            if default is not None:
                f['default'] = default

            # Min/Max values
            max_value = getattr(field, 'max_value', None)
            min_value = getattr(field, 'min_value', None)
            if max_value is not None and data_type == 'integer':
                f['minimum'] = min_value

            if max_value is not None and data_type == 'integer':
                f['maximum'] = max_value

            if data_type == 'array':
                f['items'] = items

            max_length = getattr(field, 'max_length', -1)
            min_length = getattr(field, 'min_length', -1)
            if min_length > -1:
                 f['minLength'] = min_length
            if max_length > -1:
                 f['maxLength'] = max_length

        return f




class DocumentationGenerator(DocumentationGeneratorBase):

    def __init__(self, for_user=None):
        super(DocumentationGenerator, self).__init__(for_user)

    def generate(self, apis):
        """
        Returns documentation for a list of APIs
        """
        api_docs = {}
        for api in apis:
            api_docs[api['path']] = self.get_operations(api, apis)

        return api_docs

    def get_operations(self, api, apis=None):
        """
        Returns docs for the allowed methods of an API endpoint
        """
        if apis is None:
            apis = [api]
        operations = {}

        introspector = self.get_introspector(api, apis)

        for method_introspector in introspector:
            if not isinstance(method_introspector, BaseMethodIntrospector) or \
                    method_introspector.get_http_method() == "OPTIONS":
                continue  # No one cares. I impose JSON.

            doc_parser = method_introspector.get_yaml_parser()

            operation = {
                'summary':     method_introspector.get_summary(),
                'description': method_introspector.get_notes(),
                'operationId': method_introspector.get_nickname(),
            }

            if doc_parser.yaml_error is not None:
                operation['description'] += "<pre>YAMLError:\n {err}</pre>".format(
                    err=doc_parser.yaml_error)

            response_messages = doc_parser.get_responses(method_introspector.callback)
            parameters = doc_parser.discover_parameters(
                inspector=method_introspector)

            operation['parameters'] = parameters or []

            responses = {}
            if response_messages:
                for response in response_messages:
                    r = {
                        'description': response['description'] if response['description'] is not None else "",
                    }
                    if response['schema'] is not None:
                        if isinstance(response['schema'], basestring):
                            try:
                                serializer = doc_parser.load_serializer_class(response['schema'], method_introspector.callback)
                                serializer_name = IntrospectorHelper.get_serializer_name(serializer)
                                r['schema'] = {
                                    '$ref': "#/definitions/%s" % serializer_name
                                }
                            except Exception as e:
                                logger.error(str(e))
                        else:
                            r['schema'] = response['schema']
                    if response['example'] is not None:
                        r['example'] = response['example']
                    responses[response['code']] = r
            else:
                responses['default'] = {
                    'description': 'Default response'
                }
            operation['responses'] = responses

            # tags
            tags = doc_parser.get_tags()
            if tags:
                operation['tags'] = tags

            # operation.consumes
            consumes = doc_parser.get_consumes()
            if consumes:
                operation['consumes'] = consumes
            # operation.produces
            produces = doc_parser.get_produces()
            if produces:
                operation['produces'] = produces

            # # Check if this method has been reported as returning an
            # # array response
            # if method_introspector.is_array_response:
            #     operation['items'] = {
            #         '$ref': operation['type']
            #     }
            #     operation['type'] = 'array'

            operations[method_introspector.get_http_method().lower()] = operation

        return operations

    def get_models(self, apis):
        """
        Builds a list of Swagger 'models'. These represent
        DRF serializers and their fields
        """
        serializers = self._get_serializer_set(apis)
        serializers.update(self.explicit_serializers)
        serializers.update(
            self._find_field_serializers(serializers)
        )

        models = {}

        for serializer in serializers:
            data = self._get_serializer_fields(serializer)

            # Register 2 models with different subset of properties suitable
            # for data reading and writing.
            # i.e. rest framework does not output write_only fields in response
            # or require read_only fields in complex input.

            serializer_name = IntrospectorHelper.get_serializer_name(serializer)
            # # Writing
            # # no readonly fields
            # w_name = "Write{serializer}".format(serializer=serializer_name)

            # w_properties = OrderedDict((k, v) for k, v in data['fields'].items()
            #                            if k not in data['read_only'])

            # models[w_name] = {
            #     'type': 'object',
            #     'properties': w_properties,
            #     'required': [f for f in data['required'] if f in w_properties]
            # }

            # Reading
            # no write_only fields
            r_name = serializer_name

            r_properties = OrderedDict((k, v) for k, v in data['fields'].items()
                                       if k not in data['write_only'])

            models[r_name] = {
                'type': 'object',
                'properties': r_properties,
                'required': [f for f in data['required'] if f in r_properties]
            }

        models.update(self.explicit_response_types)
        models.update(self.fields_serializers)
        return models

    def _find_field_serializers(self, serializers, found_serializers=set()):
        """
        Returns set of serializers discovered from fields
        """
        if rest_framework.VERSION >= '3.0.0':
            from rest_framework.serializers import ListSerializer, ListField

        def get_thing(field, key):
            if rest_framework.VERSION >= '3.0.0':
                if isinstance(field, ListSerializer) or isinstance(field, ListField):
                    return key(field.child)
            return key(field)

        serializers_set = set()
        for serializer in serializers:
            fields = serializer().get_fields()
            for name, field in fields.items():
                if rest_framework.VERSION >= '3.0.0' and (isinstance(field, ListSerializer) or isinstance(field, ListField)):
                    f = get_thing(field, lambda f: f)
                else:
                    f = field
                if isinstance(f, BaseSerializer) or isinstance(f, Serializer):
                    serializers_set.add(get_thing(field, lambda f: f))
                    if field not in found_serializers:
                        serializers_set.update(
                            self._find_field_serializers(
                                (get_thing(field, lambda f: f.__class__),),
                                serializers_set))

        return serializers_set


