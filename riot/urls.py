from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_palette', views.get_palette, name='get_palette') 
]
