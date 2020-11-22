from django.urls import path
from . import views

urlpatterns = [

path('carts/',views.CartsView.as_view()),
path('carts/selection/',views.SelectAllView.as_view()),
path('carts/simple/',views.CartsSimpleView.as_view()),


]