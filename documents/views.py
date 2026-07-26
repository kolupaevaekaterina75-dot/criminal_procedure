from django.shortcuts import render

from django.http import HttpResponse
from .docx_builder import build_document, DocumentGenerationError

def generate_explanation(request):
    # Это пример: данные нужно брать из формы/БД, а не хардкодить
    context = {
        "date": "26.07.2024",
        "location": "г. Москва, ул. Ленина, д. 1",
        "place": "кабинет №101",
        "start_time": "10:00",
        "end_time": "11:30",
        "full_name": "Иванов Иван Иванович",
        "birth_date": "01.01.1990",
        "birth_place": "г. Москва",
        "address": "г. Москва, ул. Пушкина, д. 10",
        "phone": "+7 (999) 123-45-67",
        "citizenship": "РФ",
        "education": "высшее",
        "marital_status": "женат",
        "employment": "ООО «Вектор»",
        "work_phone": "+7 (495) 111-22-33",
        "military_duty": "военнообязанный",
        "criminal_record": "не судим",
        "document_type": "паспорт",
        "document_number": "1234 567890",
        "explanation_text": "По существу дела могу пояснить следующее: ...",
        "signature": "И. И. Иванов",
        "investigator_name": "Петров П. П.",
        "translator_name": "",  # необязательно
        "attachments": "",      # необязательно
    }

    try:
        docx_bytes = build_document("explanation", context)
        response = HttpResponse(docx_bytes, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response["Content-Disposition"] = 'attachment; filename="explanation.docx"'
        return response
    except DocumentGenerationError as e:
        return HttpResponse(f"Ошибка генерации документа: {e}", status=400)