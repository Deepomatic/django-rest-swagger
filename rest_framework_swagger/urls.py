from django.conf.urls import url
from rest_framework_swagger.views import SwaggerApiView, SwaggerUIView


urlpatterns = [
    url(r'^$', SwaggerUIView.as_view(), name="django.swagger.base.view"),
    url(r'^api-docs/?$', SwaggerApiView.as_view(), name="django.swagger.resources.view"),
]
