from django.urls import path

from . import views

app_name = "datasets"
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.DatasetDetailView.as_view(), name='dataset_detail'),
    path('search/', views.SearchDatasetsListView.as_view(), name='search_datasets'),
    path('create_connection/', views.ConnectionCreateView.as_view(), name='create_connection'),
    path('update_connection/<int:pk>/', views.ConnectionUpdateView.as_view(), name='update_connection'),
    path('delete_connection/<int:pk>/', views.ConnectionDeleteView.as_view(), name='delete_connection'),
    path('create_query_dataset/', views.QueryDatasetCreateView.as_view(), name='create_query_dataset'),
    path('update_dataset/<int:pk>/', views.DatasetUpdateView.as_view(), name='update_dataset'),
    path('import_datasets/', views.ImportDatasetsCreateView.as_view(), name='import_datasets'),
    path('upload_datasets/', views.UploadDatasetsCreateView.as_view(), name='upload_datasets'),
    path('delete_dataset/<int:pk>/', views.DatasetDeleteView.as_view(), name='delete_dataset'),
    path('profile_history/<int:pk>/', views.ReadProfileHistory.as_view(), name='profile_history'),
    path('ajax/test_connection/', views.test_connection, name='test_connection'),
    path('ajax/update_datastore_form/', views.update_datastore_form, name='update_datastore_form'),
    path('ajax/query_preview/', views.query_preview, name='query_preview'),
    path('ajax/connection_datasets/', views.connection_datasets, name='connection_datasets'),
    path('ajax/update_profile_history/', views.update_read_profile_history, name='update_profile_history'),
    path('ajax/create_note/', views.create_note, name='create_note'),
    path('ajax/delete_note/<int:dataset_id>/<int:note_id>/', views.delete_note, name='delete_note'),
]
