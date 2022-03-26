from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.urls import include, path
import notifications.urls

from util.dropbox_util import save_dropbox_token
from util.google_util import save_google_token
from util.one_drive_util import save_one_drive_token

urlpatterns = [
    path('', include('home.urls'), name='home'),
    path('', include('saef.urls'), name='saef'),
    path('settings/', include('settings.urls'), name='settings'),
    path('jobs/', include('jobs.urls'), name='jobs'),
    path('manage/', include('datasets.urls'), name='manage'),
    path('restapi/', include('restapi.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('saveOneDriveToken/', save_one_drive_token, name='save_one_drive_token'),
    path('saveGoogleToken/', save_google_token, name='save_google_token'),
    path('saveDropboxToken/', save_dropbox_token, name='save_dropbox_token'),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
