from django.urls import path, re_path

from validate import views

urlpatterns = [
    re_path('validate/(?P<cc_num>[0-9]{6,18})', views.ValidateCard.get),
    re_path('generate/(?P<major_identifier>[0-9]{1,6})', views.CreateCard.get)]
