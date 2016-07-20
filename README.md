# Django REST Swagger

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

3. Include the rest_framework_swagger URLs to the base path of your API. If you support multiple versions of the API and the base path is of the form ```vX.Y```, ```vX``` or ```X.Y```, the versioning will be automatic if the ```version``` field (see below) is empty.

    ```python
    patterns = ('',
        ...
        url(r'^v0.5/', include('rest_framework_swagger.urls')),
    )
    ```

4. Add ```SWAGGER_SETTINGS``` to Django configuration. Example:

    ```python
    SWAGGER_SETTINGS = {
        'exclude_namespaces': [],
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
