from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('manage/', views.ManageView.as_view(), name='manage'),
    path('application', views.ApplicationView.as_view(), name='application'),
    path('application/<int:application_id>/', views.update_application, name='application_detail'),
    path('application/add/', views.add_application, name='application_add'),
    path('application_token', views.ApplicationTokenView.as_view(), name='application_token'),
    path('application_token/<int:application_token_id>/', views.update_application_token,
         name='application_token_detail'),
    path('application_token/add/', views.add_application_token, name='add_application_token'),
    path('job/', views.JobView.as_view(), name='job'),
    path('job/<int:job_id>/', views.update_job, name='job_detail'),
    path('job/add/', views.add_job, name='add_job'),
    path('connection/', views.ConnectionView.as_view(), name='connection'),
    path('connection/<int:connection_id>/', views.update_connection, name='connection_detail'),
    path('connection/add/', views.add_connection, name='add_connection'),
    path('dataset/', views.DatasetView.as_view(), name='saef_dataset'),
    path('dataset/<int:dataset_id>/', views.update_dataset, name='dataset_detail'),
    path('dataset/add/', views.add_dataset, name='add_dataset'),
    path('column/manage/<int:dataset_id>/', views.manage_column, name='manage_column'),
    path('constraint/manage/<int:dataset_id>/', views.manage_constraint, name='manage_constraint'),
    path('<int:pk>/', views.DetailDatasetView.as_view(), name='detail_dataset'),
    path('application_session', views.application_overview, name='application_session'),
    path('application_session/<int:session_pk>/', views.application_detail, name='application_session'),
    path('job_session', views.job_overview, name='job_session'),
    path('job_session/<int:session_pk>/', views.job_detail, name='job_session'),
    path('dataset_session', views.dataset_overview, name='dataset_session'),
    path('dataset_session/<int:session_pk>/', views.dataset_detail, name='dataset_session'),
]
