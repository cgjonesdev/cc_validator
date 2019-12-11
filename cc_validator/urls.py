#! /usr/bin/python
'''
This module is the url resolver that maps incoming requests represented by the
url to the views module in cc_validation/validate
'''

from django.urls import path, re_path

from validate import views

urlpatterns = [

    # Need to accept a credit card #, but since issuers use different lengths,
    # restrict length to a minimum of 7, max of 16
    re_path('validate/(?P<cc_num>[0-9]{7,16})', views.ValidateCard.get),

    # Need to accept MII's as short as 1 digit and as long as 6 from which to
    # create the rest of the numbers while checking against Luhn's
    re_path('generate/(?P<major_identifier>[0-9]{1,6})', views.CreateCard.get)]
