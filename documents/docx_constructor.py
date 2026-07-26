from docxtpl import DocxTemplate
import io

def generate_docx_from_document(document):
    # Подставь свой путь к шаблону. Лучше хранить в media/templates/
    template_path = "media/templates/explanation.docx"  # или другой шаблон
    doc = DocxTemplate(template_path)

    context = {
        "date": str(document.date),
        "location": document.location,
        "place": document.location,  # если в шаблоне {{ place }}
        "start_time": "09:00",       # можно брать из модели или формы
        "end_time": "10:00",
        "full_name": document.participant.full_name if document.participant else "Не указано",
        # добавь остальные поля, которые нужны в шаблоне
    }

    doc.render(context)

    stream = io.BytesIO()
    doc.save(stream)
    stream.seek(0)
    return stream.getvalue()