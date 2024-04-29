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
                  path('upload-file/', views.upload_file, name='upload_file'),
                  path('save-info/<str:document_id>/', views.save_info, name='save_info'),
                  path('search/', views.search, name='search'),
                  path('wallet/', views.wallet, name='wallet'),
                  path('first_page_preview/<int:document_id>/', views.first_page_preview, name='first_page_preview'),
                  # path('restricted_pdf/<int:document_id>/', views.restricted_pdf_view, name='restricted_pdf_view'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
