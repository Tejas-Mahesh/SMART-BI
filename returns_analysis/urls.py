
from django.urls import path

from . import views


urlpatterns = [

    path(
        "returns-analysis/",
        views.returns_analysis,
        name="returns_analysis",
    ),

]
