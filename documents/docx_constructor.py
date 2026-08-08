from docxtpl import DocxTemplate
import io
from pathlib import Path
from typing import Any, Dict, Optional

BASE_TEMPLATES_DIR = Path(__file__).resolve().parent / "docx_templates"

# Маппинг кода DocumentType на имя файла шаблона.
# Важно: ключи должны точно совпадать с code из DocumentType (в нижнем регистре).
TEMPLATE_FILE_MAP = {
    "inspection_protokol": "inspection_protokol.docx",
    "explanation": "explanation.docx",
    "voluntary_surrender": "voluntary_surrender.docx",
    "orm_instruction": "orm_instruction.docx",
    # добавьте остальные типы документов по аналогии
}


def get_template_path(doc_type_code: str) -> Path:
    """
    Возвращает путь к шаблону .docx по коду типа документа.
    Если код не найден в маппинге — выбрасывает FileNotFoundError.
    """
    filename = TEMPLATE_FILE_MAP.get(doc_type_code)
    if not filename:
        raise FileNotFoundError(
            f"Шаблон для типа документа '{doc_type_code}' не найден. "
            f"Доступные коды: {list(TEMPLATE_FILE_MAP.keys())}"
        )

    path = BASE_TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Файл шаблона не найден: {path}")
    return path


def generate_docx_from_document(doc: Any) -> bytes:
    """
    Генерирует .docx-файл (в виде байтов) на основе объекта Document.
    
    Ожидаемые поля документа (используются в шаблонах):
      - doc_type.code
      - case_number
      - issue_date
      - investigator.full_name
      - participant.full_name (если есть)
      - reason (если есть)
      - location (если есть)
      - и т.д.
    """
    template_path = get_template_path(doc.doc_type.code)
    tpl = DocxTemplate(template_path)

    # Формируем контекст для шаблона
    context: Dict[str, Any] = {
        "case_number": doc.case_number,
        "issue_date": doc.issue_date,
        "case_date": getattr(doc, "case_date", None),
        "article_uk_rf": getattr(doc, "article_uk_rf", ""),
        "reason": getattr(doc, "reason", ""),
        "location": getattr(doc, "location", ""),
        "place": getattr(doc, "place", ""),
        "target_action": getattr(doc, "target_action", ""),
        "items_found": getattr(doc, "items_found", ""),
        "deadline": getattr(doc, "deadline", None),
        "creator_full_name": getattr(doc, "creator_full_name", ""),
        "recipient_position": getattr(doc, "recipient_position", ""),
        "information_source": getattr(doc, "information_source", ""),
        "authority_name": getattr(doc, "authority_name", ""),
    }

    investigator = getattr(doc, "investigator", None)
    context["investigator_name"] = investigator.full_name if investigator else ""

    participant = getattr(doc, "participant", None)
    context["participant_name"] = participant.full_name if participant else ""
    context["participant_role"] = participant.role if participant else ""

    witness1 = getattr(doc, "witness1", None)
    witness2 = getattr(doc, "witness2", None)
    context["witness1_name"] = witness1.full_name if witness1 else ""
    context["witness2_name"] = witness2.full_name if witness2 else ""

    # Рендерим шаблон
    tpl.render(context)

    # Сохраняем в BytesIO и возвращаем байты
    buffer = io.BytesIO()
    tpl.save(buffer)
    return buffer.getvalue()