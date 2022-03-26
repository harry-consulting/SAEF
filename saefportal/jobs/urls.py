from django.urls import path

from . import views

app_name = "jobs"
urlpatterns = [
    path('', views.JobListView.as_view(), name='index'),
    path('delete/<int:pk>/', views.JobDeleteView.as_view(), name='delete'),
    path('create/', views.JobCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.JobUpdateView.as_view(), name='update'),
    path('run_history/<int:pk>/', views.RunHistoryReadView.as_view(), name='run_history'),
    path('trigger/<int:pk>/', views.TriggerJobView.as_view(), name='trigger'),
    path('ajax/update_task_form/', views.update_task_form, name='update_task_form')
]
