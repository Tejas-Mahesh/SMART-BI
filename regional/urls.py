from django.urls import path

from . import views


urlpatterns = [

    path(
        "regional-analysis/",
        views.regional_analysis,
        name="regional_analysis",
    ),

]