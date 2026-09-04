from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [

    path(
        "add/<slug:slug>/",
        views.add_review,
        name="add"
    ),

    path(
        "add-review/<slug:slug>/",
        views.add_review,
        name="add_review"
    ),

    path(
        "add-by-id/<int:product_id>/",
        views.add_review_by_id,
        name="add_by_id"
    ),

]