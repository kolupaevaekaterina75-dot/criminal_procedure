from pathlib import Path
from typing import Dict, Any, Optional
from docxtpl import DocxTemplate
from django.conf import settings

class DocumentGenerationError(Exception):
    pass


def build_document(
    template_name: str,
    context: Dict[str, Any],
    output_path: Optional[Path] = None,
) -> bytes:
    """
    Генерирует документ по шаблону .docx.
    
    template_name: имя файла шаблона без расширения, например "explanation"
    context: словарь данных для подстановки
    output_path: куда сохранить файл (опционально). Если None — возвращается bytes.
    
    Возвращает: bytes документа или сохраняет файл и возвращает путь.
    """

    # ВАЛИДАЦИЯ ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ
    # Для всех шаблонов обязательны: full_name, date, case_number (если есть номер дела)
    if not context.get("full_name"):
        raise DocumentGenerationError("Обязательно указать ФИО (full_name).")
    if not context.get("date"):
        raise DocumentGenerationError("Обязательно указать дату (date).")

    # Если шаблон относится к делу (поручение, рапорт и т.п.), case_number обязателен
    # Можно определять по имени шаблона или передавать флаг. Здесь — по имени шаблона.
    case_related_templates = {"assignment", "report", "case_protocol"}  # подставь свои имена шаблонов
    if template_name in case_related_templates and not context.get("case_number"):
        raise DocumentGenerationError("Для этого документа обязательно указать номер дела (case_number).")

    # ЗАМЕНА ПУСТЫХ ОБЯЗАТЕЛЬНЫХ ЗНАЧЕНИЙ НА ПРОЧЕРК
    # Пропускаем необязательные поля: если их нет — оставляем как есть (будет пусто).
    # Но если поле есть и пустое — ставим прочерк.
    for key, value in context.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            context[key] = "—"

    # ПУТЬ К ШАБЛОНУ
    # Вариант 1: шаблоны лежат в documents/templates/
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "templates" / f"{template_name}.docx"

    # Вариант 2: если шаблоны в media/templates/ (раскомментируй и используй вместо выше)
    # template_path = settings.MEDIA_ROOT / "templates" / f"{template_name}.docx"

    if not template_path.exists():
        raise DocumentGenerationError(f"Шаблон не найден: {template_path}")

    doc = DocxTemplate(str(template_path))
    doc.render(context)

    if output_path:
        doc.save(str(output_path))
        return output_path
    else:
        # Возвращаем байты, чтобы отдать через HttpResponse
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()