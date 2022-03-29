from django.urls import path

from home import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
