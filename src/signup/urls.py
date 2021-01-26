"""signup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from signup import views

urlpatterns = [
    path('', views.index, name="index"),
    path('packages/', views.packages, name="packages"),
    path('packages/<int:package_id>/', views.package, name="package"),
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    re_path('(?P<page_name>about|privacy|contact|FAQ)/', views.page, name="page"),
    path('resources/', views.resources, name="resources"),

    path('news/', views.news, name="news"),
    path('news/<int:news_id>/', views.news_item, name="news_item"),

    path('signup/<int:package_id>/', views.signup_start, name='signup_start'),
    path('signup/<int:package_id>/country/<slug:country_code>/', views.signup_banding, name='signup_banding'),
    path('signup/<int:package_id>/country/<slug:country_code>/banding/<int:banding_id>/', views.signup_data, name='signup_data'),
    path('signup/thanks/', views.signup_thanks, name='signup_thanks'),

    path('accesslog/export/<uuid:uuid>/', views.export_access_log, name='export_access_log'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
