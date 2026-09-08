from django.urls import path

from . import views


urlpatterns = [

    path(
        "marketing-analysis/",
        views.marketing_analysis,
        name="marketing_analysis",
    ),

]