# Django REST Swagger

[![build-status-badge]][build-status]
[![pypi-version]][pypi]
[![license-badge]][license]
[![docs-badge]][docs]

####An API documentation generator for Swagger UI and Django REST Framework

This project is built on the [Django REST Framework Docs](https://github.com/marcgibbons/django-rest-framework-docs) and uses the lovely [Swagger from Wordnik](http://swagger.io) as an interface. This application introspectively generates documentation based on your Django REST Framework API code. Comments are generated in combination from code analysis and comment extraction. Here are some of the features that are documented:

* API title - taken from the class name
* Methods allowed
* Serializers & fields in use by a certain method
* Field default values, minimum, maximum, read-only and required attributes
* URL parameters (ie. /product/{id})
* Field `help_text` property is used to create the description from the serializer or model.

## Quick start

1. ```pip install django-rest-swagger```

2. Add `rest_framework_swagger` to your `INSTALLED_APPS` setting:

    ```python
        INSTALLED_APPS = (
            ...
            'rest_framework_swagger',
        )
    ```

3. Include the rest_framework_swagger URLs to a path of your choice

    ```python
    patterns = ('',
        ...
        url(r'^docs/', include('rest_framework_swagger.urls')),
    )
    ```

4. Add ```SWAGGER_SETTINGS``` to Django configuration. Example:

    ```python
    SWAGGER_SETTINGS = {
        'exclude_namespaces': [],
        'api_path': '/',
        'enabled_methods': [
            'get',
            'post',
            'put',
            'patch',
            'delete'
        ],
        'api_key': '',
        'is_authenticated': False,
        'is_superuser': False,
        'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
        'permission_denied_handler': None,
        'resource_access_handler': None,
        'base_path':'helloreverb.com/docs',
        'info': {
                'contact': {
                    'name': 'API Team',
                    'email': 'apiteam@wordnik.com'
                },
                'description': 'This is a sample server Petstore server. '
                               'You can find out more about Swagger at '
                               '<a href="http://swagger.wordnik.com">'
                               'http://swagger.wordnik.com</a> '
                               'or on irc.freenode.net, #swagger. '
                               'For this sample, you can use the api key '
                               '"special-key" to test '
                               'the authorization filters',
                'license': {
                    'name': 'Apache 2.0',
                    'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
                },
                'termsOfService': 'http://helloreverb.com/terms/',
                'title': 'Swagger Sample App',
                'version': '0.1',
        },
        'doc_expansion': 'none',
    }
    ```

for more information, see the [documentation][docs].

## YAML Format for Swagger 2.x

This is an example for the new Swagger 2.x format:

```python
@api_view(["POST"])
def foo_view(request):
    """
    Your docs
    ---
    # YAML (must be separated by `---`)

    type:
      name:
        required: true
        type: string
      url:
        required: false
        type: url
      created_at:
        required: true
        type: string
        format: date-time

    serializer: .serializers.FooSerializer
    omit_serializer: false

    parameters_strategy: merge
    omit_parameters:
        - path
    parameters:
        - name: name
          description: Foobar long description goes here
          required: true
          type: string
          in: form
        - name: other_foo
          in: query
        - name: other_bar
          in: query
        - name: avatar
          type: file

    responses:
        - code: 401
          description: Not authenticated
          schema: .serializers.ErrorSerializer

    consumes:
        - application/json
        - application/xml
    produces:
        - application/json
        - application/xml
    """
    ...
```

## Requirements
* Python (2.6.5+, 2.7, 3.2, 3.3, 3.4)
* Django (1.5.5+, 1.6, 1.7, 1.8)
* Django REST framework (2.3.8+)
* PyYAML (3.10+)

## Bugs & Contributions
Please report bugs by opening an issue

Contributions are welcome and are encouraged!

## Special Thanks
Thanks to [BNOTIONS](http://www.bnotions.com) for sponsoring initial development time.

Many thanks to Tom Christie & all the contributors who have developed [Django REST Framework](http://django-rest-framework.org/)

## Contributors
* Marc Gibbons (@marcgibbons)
* Geraldo Andrade (@quein)
* Vítek Pliska (@whit)
* Falk Schuetzenmeister (@postfalk)
* Lukas Hetzenecker (@lukas-hetzenecker)
* David Wolever (@wolever)
* Brian Moe (@bmoe)
* Ian Martin (@aztechian)
* @pzrq
* @jfelectron
* Warnar Boekkooi (@boekkooi)
* Darren Thompson (@WhiteDawn)
* Lukasz Balcerzak (@lukaszb)
* David Newgas (@davidn)
* Bozidar Benko (@bbenko)
* @pySilver


### Django REST Framework Docs contributors:

* Scott Mountenay (@scottmx81)
* @swistakm
* Peter Baumgartner (@ipmb)
* Marlon Bailey (@avinash240)


[build-status-badge]: https://travis-ci.org/marcgibbons/django-rest-swagger.svg?branch=master
[build-status]: https://travis-ci.org/marcgibbons/django-rest-swagger
[pypi-version]: https://img.shields.io/pypi/v/django-rest-swagger.svg
[pypi]: https://pypi.python.org/pypi/django-rest-swagger
[license-badge]: https://img.shields.io/pypi/l/django-rest-swagger.svg
[license]: https://pypi.python.org/pypi/django-rest-swagger/
[docs-badge]: https://readthedocs.io/projects/django-rest-swagger/badge/
[docs]: http://django-rest-swagger.readthedocs.io/
