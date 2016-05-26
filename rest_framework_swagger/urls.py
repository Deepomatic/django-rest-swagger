from django.conf.urls import url
from rest_framework_swagger.views import Swagger1_2ResourcesView, Swagger1_2ApiView, Swagger2_0ApiView, SwaggerUIView


urlpatterns = [
    url(r'^$', SwaggerUIView.as_view(), name="django.swagger.base.view"),
    url(r'^api-docs/v1\.2/$', Swagger1_2ResourcesView.as_view(), name="django.swagger.resources.view"),
    url(r'^api-docs/v1\.2/(?P<path>.*)/?$', Swagger1_2ApiView.as_view(), name='django.swagger.api.view'),
    url(r'^api-docs/v2\.0/$', Swagger2_0ApiView.as_view(), name="django.swagger.resources.view"),
]
