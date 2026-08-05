from docxtpl import DocxTemplate
import io
from pathlib import Path
from typing import Any, Dict, Optional

# Путь к шаблонам: папка docx_templates лежит рядом с этим файлом (в documents/)
BASE_TEMPLATES_DIR = Path(__file__).resolve().parent / "docx_templates"


def get_template_path(doc_type_value) -> Path:
    """
    Возвращает абсолютный путь к шаблону .docx.
    Поддерживает: строку, объект с .code, объект с .name.
    Имена файлов шаблонов должны быть в формате: <code>.docx, например inspection_protokol.docx
    """
    if doc_type_value is None:
        raise ValueError("doc_type не может быть None")

    code = None

    if isinstance(doc_type_value, str):
        code = doc_type_value
    elif hasattr(doc_type_value, "code"):
        code = doc_type_value.code
        if not code:
            raise ValueError("Атрибут .code пуст")
    elif hasattr(doc_type_value, "name"):
        code = doc_type_value.name
        if not code:
            raise ValueError("Атрибут .name пуст")
    else:
        raise ValueError(
            "Не удалось определить код типа документа. Ожидается строка или объект с .code/.name"
        )

    # Нормализация: нижний регистр, без пробелов, заменяем пробелы на _
    code = str(code).strip().lower().replace(" ", "_")

    path = BASE_TEMPLATES_DIR / f"{code}.docx"
    path = path.resolve()

    if not path.is_file():
        available = [p.name for p in BASE_TEMPLATES_DIR.iterdir() if p.is_file()]
        raise FileNotFoundError(
            f"Шаблон не найден: {path}\n"
            f"Ожидалось имя файла: {code}.docx\n"
            f"Проверьте, что файл лежит в: {BASE_TEMPLATES_DIR}\n"
            f"Доступные файлы в папке: {available}"
        )

    return path


def _get_person_data(person: Optional[Any]) -> Dict[str, str]:
    """
    Безопасное получение данных о человеке.
    Возвращает словарь с полными данными, даже если объект неполный.
    """
    if person is None:
        return {
            "full_name": "Не указано",
            "position": "Не указано",
            "department": "Не указано"
        }

    full_name = getattr(person, "full_name", None) or getattr(person, "name", "")
    if not full_name or (isinstance(full_name, str) and full_name.strip() == ""):
        full_name = "Не указано"

    position = getattr(person, "position", None) or getattr(person, "role", None)
    if position is None or (isinstance(position, str) and position.strip() == ""):
        position = "Не указано"

    department = getattr(person, "department", None)
    if department is None or (isinstance(department, str) and department.strip() == ""):
        department = "Не указано"

    return {
        "full_name": full_name,
        "position": position,
        "department": department
    }


def build_context_for_document(document: Any) -> Dict[str, Any]:
    """
    Собирает контекст для docxtpl, строго соответствующий полям в шаблонах.
    Для inspection_protokol.docx используются переменные:
      {{ date_day }}, {{ date_month }}, {{ date_year }}
      {{ start_time }}, {{ start_minutes }} и т.д.
    
    Если у документа есть специфичные поля (например, для протокола осмотра),
    они будут заполнены; если нет — подставляется безопасное значение.
    """

    doc_type = getattr(document, "doc_type", None)

    # Получаем код типа документа (он же имя файла шаблона без .docx)
    doc_code = None
    if doc_type is not None:
        if hasattr(doc_type, "code") and doc_type.code:
            doc_code = str(doc_type.code).strip().lower().replace(" ", "_")
        elif hasattr(doc_type, "name") and doc_type.name:
            doc_code = str(doc_type.name).strip().lower().replace(" ", "_")

    participant = getattr(document, "participant", None)
    investigator = getattr(document, "investigator", None)

    p_data = _get_person_data(participant)
    i_data = _get_person_data(investigator)

    issue_date = getattr(document, "issue_date", None)
    date_day = date_month = date_year = "—"
    if issue_date is not None:
        try:
            if isinstance(issue_date, str):
                # Если дата пришла строкой, можно попробовать распарсить, но пока просто ставим прочерк
                date_day = date_month = date_year = "—"
            else:
                date_day = str(issue_date.day).zfill(2)
                date_month = issue_date.strftime("%B")  # полное название месяца, например October
                date_year = str(issue_date.year)
        except Exception:
            date_day = date_month = date_year = "—"

    location = getattr(document, "location", None) or "Не указано"

    def get_field(obj, field, default="—"):
        val = getattr(obj, field, None)
        if val is None:
            return default
        if isinstance(val, str) and val.strip() == "":
            return default
        return val

    # Для протокола осмотра места происшествия используем отдельные поля,
    # чтобы точно соответствовать шаблону с {{ date_day }} и т.п.
    start_time = get_field(document, "start_time", "—")
    start_minutes = get_field(document, "start_minutes", "—")
    end_time = get_field(document, "end_time", "—")
    end_minutes = get_field(document, "end_minutes", "—")

    context = {
        # Дата по частям — для шаблона inspection_protokol
        "date_day": date_day,
        "date_month": date_month,
        "date_year": date_year,

        # Место составления (в шаблоне есть строка "(место составления)")
        "place": location,

        # Время начала и окончания
        "start_time": start_time,
        "start_minutes": start_minutes,
        "end_time": end_time,
        "end_minutes": end_minutes,

        # Следователь
        "investigator_position": i_data["position"],
        "investigator_rank": get_field(document, "investigator_rank", "—"),
        "investigator_name": i_data["full_name"],

        # Сообщение и прибытие
        "message_from": get_field(document, "message_from", "—"),
        "message_about": get_field(document, "message_about", "—"),
        "arrived_to": get_field(document, "arrived_to", "—"),

        # Понятые
        "witness1_full_name": get_field(document, "witness1_full_name", "—"),
        "witness1_address": get_field(document, "witness1_address", "—"),
        "witness2_full_name": get_field(document, "witness2_full_name", "—"),
        "witness2_address": get_field(document, "witness2_address", "—"),

        # Специалист и иные участники
        "specialist_full_name": get_field(document, "specialist_full_name", "—"),
        "specialist_position": get_field(document, "specialist_position", "—"),
        "other_participants": get_field(document, "other_participants", "—"),

        # Объект осмотра и условия
        "object_inspection": get_field(document, "object_inspection", "—"),
        "technical_means": get_field(document, "technical_means", "—"),
        "weather_conditions": get_field(document, "weather_conditions", "—"),
        "lighting_conditions": get_field(document, "lighting_conditions", "—"),

        # Результаты и методы
        "inspection_results": get_field(document, "inspection_results", "—"),
        "examination_methods": get_field(document, "examination_methods", "—"),
        "seized_items": get_field(document, "seized_items", "—"),

        # Ознакомление и замечания
        "reading_method": get_field(document, "reading_method", "—"),
        "remarks": get_field(document, "remarks", "—"),

        # Подписи (обычно пустые, инициалы отдельно)
        "witness1_signature": "",
        "witness1_initials": get_field(document, "witness1_initials", "—"),
        "witness2_signature": "",
        "witness2_initials": get_field(document, "witness2_initials", "—"),
        "specialist_signature": "",
        "specialist_initials": get_field(document, "specialist_initials", "—"),
        "other_participants_signatures": get_field(document, "other_participants_signatures", ""),
        "investigator_signature": "",
        "investigator_initials": get_field(document, "investigator_initials", "—"),

        # Поля, которые могут использоваться в других шаблонах
        "doc_type": doc_code or "Не указан",
        "title": get_field(document, "title", "Без названия"),
        "content_text": get_field(document, "content_text", ""),
    }
    return context


def generate_docx_from_document(document: Any) -> bytes:
    """
    Генерирует DOCX из документа и возвращает байты.
    Шаблон выбирается по doc_type (code или name), ожидается файл <code>.docx в docx_templates.
    """
    doc_type_val = getattr(document, "doc_type", None)
    if doc_type_val is None:
        raise ValueError("У документа отсутствует поле doc_type")

    template_path = get_template_path(doc_type_val)

    try:
        tpl = DocxTemplate(str(template_path))
    except Exception as e:
        raise RuntimeError(f"Не удалось загрузить шаблон DOCX: {template_path}. Ошибка: {e}") from e

    context = build_context_for_document(document)

    try:
        tpl.render(context)
    except Exception as e:
        # Чтобы было проще отлаживать: какая переменная не нашлась в шаблоне
        raise RuntimeError(f"Ошибка при рендере шаблона: {e}") from e

    buffer = io.BytesIO()
    try:
        tpl.save(buffer)
    except Exception as e:
        raise RuntimeError(f"Ошибка при сохранении DOCX в буфер: {e}") from e

    return buffer.getvalue()