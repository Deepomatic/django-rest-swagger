VERSION = '0.3.7'

DEFAULT_SWAGGER_SETTINGS = {
    'swagger_version': '1.2',
    'exclude_url_names': [],
    'exclude_namespaces': [],
    'api_version': '',
    'api_path': '/',
    'api_key': '',
    'relative_paths': False,
    'token_type': 'Token',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'is_authenticated': False,
    'is_superuser': False,
    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    'permission_denied_handler': None,
    'resource_access_handler': None,
    'template_path': 'rest_framework_swagger/index.html',
    'doc_expansion': 'none',
}


class SwaggerSchemeException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

def validate_info_1_2(provided_settings):
    for key in ['title', 'description']:
        if key not in provided_settings['info']:
            raise SwaggerSchemeException("Missing key '%s' for field 'info' in 'DEFAULT_SWAGGER_SETTINGS'. See https://github.com/swagger-api/swagger-spec/blob/master/versions/1.2.md#513-info-object" % key)

def validate_info_2_0(provided_settings):
    for key in ['title', 'version']:
        if key not in provided_settings['info']:
            raise SwaggerSchemeException("Missing key '%s' for field 'info' in 'DEFAULT_SWAGGER_SETTINGS'. See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#infoObject" % key)


from django.conf import settings
from django.test.signals import setting_changed

def load_settings(provided_settings):
    global SWAGGER_SETTINGS
    SWAGGER_SETTINGS = provided_settings

    for key, value in DEFAULT_SWAGGER_SETTINGS.items():
        if key not in SWAGGER_SETTINGS:
            SWAGGER_SETTINGS[key] = value

    # Validate SWAGGER_SETTINGS
    if SWAGGER_SETTINGS['swagger_version'] not in ['1.2', '2.0']:
        raise SwaggerSchemeException("'swagger_version' should be '1.2' or '2.0'")
    if 'info' in SWAGGER_SETTINGS:
        if SWAGGER_SETTINGS['swagger_version'] == '1.2':
            validate_info_1_2(SWAGGER_SETTINGS)
        else:
            if 'api_version' in SWAGGER_SETTINGS:
                raise SwaggerSchemeException("Extra field 'api_version' for Swagger 2.0")
            validate_info_2_0(SWAGGER_SETTINGS)


def reload_settings(*args, **kwargs):
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'SWAGGER_SETTINGS':
        load_settings(value)

load_settings(getattr(settings,
                      'SWAGGER_SETTINGS',
                      DEFAULT_SWAGGER_SETTINGS))
setting_changed.connect(reload_settings)

