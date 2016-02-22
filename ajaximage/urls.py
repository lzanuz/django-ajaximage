#-*- coding: utf-8 -*-

from django.conf.urls import url


patterns = [

    url(
        '^upload/(?P<upload_to>.*)/(?P<max_width>\d+)/(?P<max_height>\d+)/(?P<crop>\d+)',
        'ajaximage.views.ajaximage',
        name='ajaximage'
    ),

]
