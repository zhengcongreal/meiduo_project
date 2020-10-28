from django.urls import path
from . import views
urlpatterns = [
path('areas/',views.ProvinceAreasView.as_view()),
path('areas/<int:pk>/',views.SubAreasView.as_view()),
]