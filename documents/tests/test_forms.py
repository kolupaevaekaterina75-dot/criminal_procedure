import pytest
from documents.forms import DocumentForm
from documents.models import Document, Participant, DocumentType


@pytest.mark.django_db
def test_document_form_required_fields_missing():
    """
    Проверяем, что при отсутствии title, doc_type, issue_date форма не валидна.
    Передаём пустой словарь: Django должен выдать ошибки на все обязательные поля.
    """
    data = {}  # пустой dict — это «ничего не передано», тогда обязательность сработает корректно
    form = DocumentForm(data=data)
    assert not form.is_valid(), "Форма должна быть невалидной при отсутствии обязательных полей"

    # Ошибки по конкретным полям
    assert "title" in form.errors, "Должна быть ошибка валидации для поля title"
    assert "doc_type" in form.errors, "Должна быть ошибка валидации для поля doc_type"
    assert "issue_date" in form.errors, "Должна быть ошибка валидации для поля issue_date"


@pytest.mark.django_db
def test_document_form_explanation_requires_participant():
    """
    Для типа 'explanation' форма должна требовать participant.
    Это требование должно быть реализовано в clean() формы.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code='explanation',
        defaults={'name': 'Объяснение'}
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

    # Вариант 1: participant отсутствует — форма невалидна
    data_no_participant = {
        "title": "Объяснение без участника",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
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
        "issue_date": "2025-12-10",
        "participant": participant.pk,
    }
    form_with_participant = DocumentForm(data=data_with_participant)
    assert form_with_participant.is_valid(), f"Форма не валидна: {form_with_participant.errors}"


@pytest.mark.django_db
def test_document_form_inspection_protokol_requires_location():
    """
    Для типа 'inspection_protokol' форма должна требовать location.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code='inspection_protokol',
        defaults={'name': 'Протокол осмотра'}
    )

    data_no_location = {
        "title": "Протокол без места",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
        # location намеренно не передан
    }
    form_no_location = DocumentForm(data=data_no_location)
    assert not form_no_location.is_valid()
    assert "location" in form_no_location.errors, (
        "Для протокола осмотра должна быть ошибка по полю location"
    )

    data_with_location = {
        "title": "Валидный протокол осмотра",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
        "location": "ул. Ленина, д. 1",
    }
    form_with_location = DocumentForm(data=data_with_location)
    assert form_with_location.is_valid(), f"Форма не валидна: {form_with_location.errors}"


@pytest.mark.django_db
def test_document_form_orm_instruction_requires_target_action():
    """
    Для типа 'orm_instruction' форма должна требовать target_action.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code='orm_instruction',
        defaults={'name': 'Поручение ОРМ'}
    )

    data_no_target = {
        "title": "Поручение без действия",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
        # target_action намеренно не передан
    }
    form_no_target = DocumentForm(data=data_no_target)
    assert not form_no_target.is_valid()
    assert "target_action" in form_no_target.errors, (
        "Для поручения должна быть ошибка по полю target_action"
    )

    data_with_target = {
        "title": "Валидное поручение ОРМ",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
        "target_action": "Провести опрос свидетелей",
    }
    form_with_target = DocumentForm(data=data_with_target)
    assert form_with_target.is_valid(), f"Форма не валидна: {form_with_target.errors}"


@pytest.mark.django_db
def test_document_form_voluntary_surrender_requires_reason():
    """
    Для типа 'voluntary_surrender' форма должна требовать reason.
    """
    doc_type, _ = DocumentType.objects.get_or_create(
        code='voluntary_surrender',
        defaults={'name': 'Явка с повинной'}
    )

    data_no_reason = {
        "title": "Явка без причины",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
        # reason намеренно не передан
    }
    form_no_reason = DocumentForm(data=data_no_reason)
    assert not form_no_reason.is_valid()
    assert "reason" in form_no_reason.errors, (
        "Для явки с повинной должна быть ошибка по полю reason"
    )

    data_with_reason = {
        "title": "Валидная явка с повинной",
        "doc_type": doc_type.pk,
        "issue_date": "2025-12-10",
        "reason": "Сознался в совершении преступления",
    }
    form_with_reason = DocumentForm(data=data_with_reason)
    assert form_with_reason.is_valid(), f"Форма не валидна: {form_with_reason.errors}"