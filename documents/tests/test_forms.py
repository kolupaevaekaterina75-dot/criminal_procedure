import pytest
from django.utils import timezone
from datetime import date

from documents.forms import DocumentForm
from documents.models import DocumentType, Participant


@pytest.mark.django_db
def test_document_form_required_fields_missing():
    """
    Проверяем, что при отсутствии обязательных полей (title, doc_type) форма невалидна.
    Остальные поля могут быть необязательными или иметь default — не проверяем их как обязательные.
    """
    data = {}  # пустой dict — ничего не передано
    form = DocumentForm(data=data)
    assert not form.is_valid(), "Форма должна быть невалидной при отсутствии обязательных полей"

    # Проверяем ошибки только по реально обязательным полям формы
    assert "title" in form.errors, "Должна быть ошибка валидации для поля title"
    assert "doc_type" in form.errors, "Должна быть ошибка валидации для поля doc_type"


@pytest.mark.django_db
def test_document_form_explanation_requires_participant():
    """
    Для типа 'explanation' форма должна требовать participant (проверка через clean()).
    При этом остальные обязательные поля (case_number, case_date, issue_date, status)
    должны быть переданы, чтобы тест проверял именно participant.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code="explanation",
        defaults={"name": "Объяснение"}
    )

    participant, _ = Participant.objects.get_or_create(
        full_name="Иванов И.И.",
        defaults={
            "role": "witness",
            "side": "other",
            "birth_date": None,
            "phone": "79990000001",
        }
    )

    today = date.today().isoformat()

    # Вариант 1: participant отсутствует — форма невалидна
    data_no_participant = {
        "title": "Объяснение без участника",
        "doc_type": doc_type.pk,
        "case_number": "12345/2026",
        "case_date": "2026-01-01",
        "issue_date": today,
        "status": "draft",
        # participant намеренно не передан
    }
    form_no_participant = DocumentForm(data=data_no_participant)
    assert not form_no_participant.is_valid()
    assert "participant" in form_no_participant.errors, (
        "Для объяснения должна быть ошибка по полю participant"
    )

    # Вариант 2: participant есть — форма валидна (если другие требования выполнены)
    data_with_participant = {
        "title": "Валидное объяснение",
        "doc_type": doc_type.pk,
        "participant": participant.pk,
        "case_number": "12345/2026",
        "case_date": "2026-01-01",
        "issue_date": today,
        "status": "draft",
    }
    form_with_participant = DocumentForm(data=data_with_participant)
    assert form_with_participant.is_valid(), f"Форма не валидна: {form_with_participant.errors}"


@pytest.mark.django_db
def test_document_form_inspection_protokol_requires_location():
    """
    Для типа 'inspection_protokol' форма должна требовать location (проверка через clean()).
    ВАЖНО: поле location должно быть объявлено в модели Document. Если его нет — тест будет падать.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code="inspection_protokol",
        defaults={"name": "Протокол осмотра"}
    )

    today = date.today().isoformat()

    # Вариант 1: location отсутствует — форма невалидна
    data_no_location = {
        "title": "Протокол без места",
        "doc_type": doc_type.pk,
        "case_number": "12346/2026",
        "case_date": "2026-01-02",
        "issue_date": today,
        "status": "draft",
        # location намеренно не передан
    }
    form_no_location = DocumentForm(data=data_no_location)
    assert not form_no_location.is_valid()
    assert "location" in form_no_location.errors, (
        "Для протокола осмотра должна быть ошибка по полю location"
    )

    # Вариант 2: location есть — форма валидна
    data_with_location = {
        "title": "Валидный протокол осмотра",
        "doc_type": doc_type.pk,
        "location": "ул. Ленина, д. 1",
        "case_number": "12346/2026",
        "case_date": "2026-01-02",
        "issue_date": today,
        "status": "draft",
    }
    form_with_location = DocumentForm(data=data_with_location)
    assert form_with_location.is_valid(), f"Форма не валидна: {form_with_location.errors}"


@pytest.mark.django_db
def test_document_form_orm_instruction_requires_target_action():
    """
    Для типа 'orm_instruction' форма должна требовать target_action (проверка через clean()).
    ВАЖНО: поле target_action должно быть объявлено в модели Document.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code="orm_instruction",
        defaults={"name": "Поручение ОРМ"}
    )

    today = date.today().isoformat()

    # Вариант 1: target_action отсутствует — форма невалидна
    data_no_target = {
        "title": "Поручение без действия",
        "doc_type": doc_type.pk,
        "case_number": "12347/2026",
        "case_date": "2026-01-03",
        "issue_date": today,
        "status": "draft",
        # target_action намеренно не передан
    }
    form_no_target = DocumentForm(data=data_no_target)
    assert not form_no_target.is_valid()
    assert "target_action" in form_no_target.errors, (
        "Для поручения должна быть ошибка по полю target_action"
    )

    # Вариант 2: target_action есть — форма валидна
    data_with_target = {
        "title": "Валидное поручение ОРМ",
        "doc_type": doc_type.pk,
        "target_action": "Провести опрос свидетелей",
        "case_number": "12347/2026",
        "case_date": "2026-01-03",
        "issue_date": today,
        "status": "draft",
    }
    form_with_target = DocumentForm(data=data_with_target)
    assert form_with_target.is_valid(), f"Форма не валидна: {form_with_target.errors}"


@pytest.mark.django_db
def test_document_form_voluntary_surrender_requires_reason():
    """
    Для типа 'voluntary_surrender' форма должна требовать reason (проверка через clean()).
    ВАЖНО: поле reason должно быть объявлено в модели Document.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code="voluntary_surrender",
        defaults={"name": "Явка с повинной"}
    )

    today = date.today().isoformat()

    # Вариант 1: reason отсутствует — форма невалидна
    data_no_reason = {
        "title": "Явка без причины",
        "doc_type": doc_type.pk,
        "case_number": "12348/2026",
        "case_date": "2026-01-04",
        "issue_date": today,
        "status": "draft",
        # reason намеренно не передан
    }
    form_no_reason = DocumentForm(data=data_no_reason)
    assert not form_no_reason.is_valid()
    assert "reason" in form_no_reason.errors, (
        "Для явки с повинной должна быть ошибка по полю reason"
    )

    # Вариант 2: reason есть — форма валидна
    data_with_reason = {
        "title": "Валидная явка с повинной",
        "doc_type": doc_type.pk,
        "reason": "Сознался в совершении преступления",
        "case_number": "12348/2026",
        "case_date": "2026-01-04",
        "issue_date": today,
        "status": "draft",
    }
    form_with_reason = DocumentForm(data=data_with_reason)
    assert form_with_reason.is_valid(), f"Форма не валидна: {form_with_reason.errors}"