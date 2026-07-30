from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Участники: оставляем CBV как основной список (соответствует name='participant_list')
    path('participants/', views.ParticipantList.as_view(), name='participant_list'),
    # Если позже понадобится отдельная функция-view, можно добавить отдельный URL с другим name

    # Документы: список делаем корневым для /docs/
    path('', views.document_list, name='document_list'),          # /docs/ → список документов
    path('create/', views.document_create, name='document_create'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/download/', views.document_download, name='document_download'),

    # Шаг 9: отчёт по количеству документов по участникам
    path('report/documents-by-participant/', views.report_documents_by_participant, name='report_documents_by_participant'),
]
