from docxtpl import DocxTemplate
import io
from pathlib import Path
from django.conf import settings

# Базовый путь к папке с шаблонами (относительно приложения documents)
BASE_TEMPLATES_DIR = Path(__file__).resolve().parent / "docx_templates"

def get_template_path(doc_type: str) -> Path:
    """
    doc_type должен совпадать с тем, что хранится в модели Document.doc_type.
    Например: 'explanation', 'inspection_protokol', 'orm_instruction', 'report', 'voluntary_surrender'
    """
    mapping = {
        "explanation": "explanation.docx",
        "inspection_protokol": "inspection_protokol.docx",
        "orm_instruction": "orm_instruction.docx",
        "report": "report.docx",
        "voluntary_surrender": "voluntary_surrender.docx",
    }
    filename = mapping.get(doc_type)
    if not filename:
        raise ValueError(f"Неизвестный тип документа: {doc_type}")
    return BASE_TEMPLATES_DIR / filename

def generate_docx_from_document(document):
    template_path = get_template_path(document.doc_type)

    if not template_path.exists():
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")

    doc = DocxTemplate(template_path)

    # Универсальный контекст: подставляй сюда все поля, которые встречаются в шаблонах
    context = {
        "date": str(document.date) if document.date else "",
        "location": document.location or "",
        "place": document.location or "",          # если в шаблоне {{ place }}
        "start_time": getattr(document, "start_time", "09:00") or "09:00",
        "end_time": getattr(document, "end_time", "10:00") or "10:00",
        "full_name": (document.participant.full_name if document.participant else "Не указано") or "",
        # Если в шаблонах есть другие общие поля — добавь их здесь
    }

    # Специфичные поля для разных типов документов (если нужны)
    if document.doc_type == "inspection_protokol":
        context["object_description"] = getattr(document, "object_description", "") or ""
        context["items_found"] = getattr(document, "items_found", "") or ""

    if document.doc_type == "orm_instruction":
        context["target_action"] = getattr(document, "target_action", "") or ""
        context["deadline"] = str(getattr(document, "deadline", "")) if getattr(document, "deadline", None) else ""

    if document.doc_type == "voluntary_surrender":
        context["reason"] = getattr(document, "reason", "") or ""

    # Если в моделях есть другие поля под конкретные шаблоны — добавляй по аналогии

    doc.render(context)

    stream = io.BytesIO()
    doc.save(stream)
    stream.seek(0)
    return stream.getvalue()