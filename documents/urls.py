from django.urls import path
from . import views

urlpatterns = [
    # Участники
    path('participants/', views.ParticipantList.as_view(), name='participant_list'),
    # Если participant_create ещё не создан — закомментируйте эту строку, пока не добавите функцию
    # path('participants/create/', views.participant_create, name='participant_create'),

    # Документы
    path('documents/', views.document_list, name='document_list'),
    path('documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
]