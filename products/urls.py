from django.urls import path

from . import views


urlpatterns = [

    path(
        "product-intelligence/",
        views.product_intelligence,
        name="product_intelligence",
    ),

]