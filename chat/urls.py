from django.conf.urls.static import static
from django.urls import path, re_path

from PFE_NoteShare import settings
from . import views

app_name = 'chat'
urlpatterns = [
    path('<int:id>/', views.chatPage, name='chatPage'),
]
