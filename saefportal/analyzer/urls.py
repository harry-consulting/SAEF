from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='analyzer_index'),
    path('get_task_info/', views.get_task_info, name='get_task_info'),
    path('get_dataset_result/', views.get_dataset_result, name='get_dataset_result'),
]