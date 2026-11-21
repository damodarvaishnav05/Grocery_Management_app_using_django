from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.index, name='index'),
    path('add-recipe-to-cart/', views.add_recipe_to_cart, name='add_recipe_to_cart'),
]
