#-*- coding: utf-8 -*-

from django.conf.urls import url

from ajaximage import views


urlpatterns = [

    url(
        '^upload/(?P<upload_to>.*)/(?P<max_width>\d+)/(?P<max_height>\d+)/(?P<crop>\d+)',
        views.ajaximage,
        name='ajaximage'
    ),

]
