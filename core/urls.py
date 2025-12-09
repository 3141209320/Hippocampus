from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('papers/', views.exam_list, name='exam_list'),
    path('papers/upload/', views.upload_exam, name='upload_exam'),
    path('papers/<int:paper_id>/delete/', views.delete_paper, name='delete_paper'),
    path('exam/<int:paper_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:paper_id>/preview/', views.paper_preview, name='paper_preview'),
    
    path('mistakes/', views.mistake_list, name='mistake_list'),
    
    # API endpoints
    path('api/sync_progress/', views.sync_progress, name='sync_progress'),
    path('api/submit_answer/', views.submit_answer, name='submit_answer'),
    path('api/toggle_mistake/', views.toggle_mistake, name='toggle_mistake'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
