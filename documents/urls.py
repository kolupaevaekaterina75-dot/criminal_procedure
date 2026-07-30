from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Участники
    path('participants/', views.ParticipantList.as_view(), name='participant_list'),
    # path('participants/create/', views.participant_create, name='participant_create'),  # раскомментируй, когда создашь view

    # Документы: список делаем корневым для /docs/
    path('', views.document_list, name='document_list'),          # теперь /docs/ → список документов
    path('create/', views.document_create, name='document_create'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
]
