from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_palette', views.get_palette, name='get_palette'),
    path('get_and_store_summoner_data', views.get_and_store_summoner_data, name='get_and_store_summoner_data')
]
