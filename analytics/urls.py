from django.urls import path

from . import views


urlpatterns = [

    path(
        "business-overview/",
        views.business_overview,
        name="business_overview",
    ),

]