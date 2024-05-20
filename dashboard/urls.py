from django.conf.urls.static import static
from django.urls import path, re_path

from PFE_NoteShare import settings
from . import views

app_name = 'dashboard'
urlpatterns = [
                  path('', views.index, name='index'),
                  path('file-manager/', views.file_manager, name='file_manager'),
                  re_path(r'^file-manager/(?P<directory>.*)?/$', views.file_manager, name='file_manager'),
                  path('delete-file/<str:document_id>/', views.delete_file, name='delete_file'),
                  path('download-file/<str:document_id>/', views.download_file, name='download_file'),
                  path('delete-school/<str:school_id>/', views.delete_school, name='delete_school'),
                  path('delete-doct/<str:doct_id>/', views.delete_doct, name='delete_doct'),
                  path('delete-subject/<str:subject_id>/', views.delete_subject, name='delete_subject'),
                  path('upload-file/', views.upload_file, name='upload_file'),
                  path('save-info/<str:document_id>/', views.save_info, name='save_info'),
                  path('search/', views.search, name='search'),
                  path('wallet/', views.wallet, name='wallet'),
                  path('first_page_preview/<int:document_id>/', views.first_page_preview, name='first_page_preview'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
