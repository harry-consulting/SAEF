from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from . import views

app_name = "settings"
urlpatterns = [
    path('<int:pk>/', views.SettingsUpdateView.as_view(), name='settings'),
    path('create_datalake_connection/', views.DatalakeConnectionCreateView.as_view(),
         name="create_datalake_connection"),
    path('create_datalake_connection/<str:redirect>/', views.DatalakeConnectionCreateView.as_view(),
         name="create_datalake_connection"),
    path('update_datalake_connection/', views.DatalakeConnectionUpdateView.as_view(),
         name="update_datalake_connection"),
    path('delete_datalake_connection/<int:pk>/', views.DatalakeConnectionDeleteView.as_view(),
         name='delete_datalake_connection'),
    path('ajax/update_datalake_form/', views.update_datalake_form, name="update_datalake_form"),
    path('ajax/add_contact/', views.add_contact, name='add_contact'),
    path('ajax/delete_contact/<int:contact_id>/', views.delete_contact, name='delete_contact')
]

urlpatterns += staticfiles_urlpatterns()
