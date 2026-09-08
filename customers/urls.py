from django.urls import path

from . import views


urlpatterns = [

    path(
        "customer-intelligence/",
        views.customer_intelligence,
        name="customer_intelligence",
    ),

]