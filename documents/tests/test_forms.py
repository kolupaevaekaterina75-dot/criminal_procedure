import pytest
from django.core.exceptions import ValidationError
from documents.forms import DocumentForm
from documents.models import Document, Participant


@pytest.mark.django_db
def test_document_form_required_fields_missing():
    """
    Проверяем, что при отсутствии title, doc_type, date форма не валидна
    и выбрасывает ожидаемую ошибку.
    """
    data = {
        "title": "",
        "doc_type": "",
        "date": None,
    }
    form = DocumentForm(data=data)
    assert not form.is_valid()
    assert "Обязательно заполните название документа, тип и дату." in form.errors.get("__all__", [])


@pytest.mark.django_db
def test_document_form_all_required_present():
    """
    Проверяем, что форма валидна, когда title, doc_type, date заполнены.
    Это покрывает ветку, где общая проверка проходит.
    """
    participant = Participant.objects.create(full_name="Иванов И.И.")
    data = {
        "title": "Протокол",
        "doc_type": "inspection_protokol",
        "date": "2026-08-01",
        "participant": participant.pk,
        "location": "ул. Ленина, 1",
    }
    form = DocumentForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_document_form_explanation_requires_participant():
    """
    Для doc_type == 'explanation' обязательно указать participant.
    """
    data = {
        "title": "Объяснение",
        "doc_type": "explanation",
        "date": "2026-08-01",
        # participant отсутствует
    }
    form = DocumentForm(data=data)
    assert not form.is_valid()
    assert "Для объяснения обязательно укажите участника." in form.errors.get("participant", [])


@pytest.mark.django_db
def test_document_form_inspection_protokol_requires_location():
    """
    Для doc_type == 'inspection_protokol' обязательно указать location.
    """
    data = {
        "title": "Протокол осмотра",
        "doc_type": "inspection_protokol",
        "date": "2026-08-01",
        # location отсутствует
    }
    form = DocumentForm(data=data)
    assert not form.is_valid()
    assert "Для протокола осмотра места происшествия обязательно укажите место." in form.errors.get("location", [])


@pytest.mark.django_db
def test_document_form_orm_instruction_requires_target_action():
    """
    Для doc_type == 'orm_instruction' обязательно указать target_action.
    """
    data = {
        "title": "Поручение",
        "doc_type": "orm_instruction",
        "date": "2026-08-01",
        # target_action отсутствует
    }
    form = DocumentForm(data=data)
    assert not form.is_valid()
    assert "Для поручения укажите целевое действие." in form.errors.get("target_action", [])


@pytest.mark.django_db
def test_document_form_voluntary_surrender_requires_reason():
    """
    Для doc_type == 'voluntary_surrender' обязательно указать reason.
    """
    data = {
        "title": "Явка с повинной",
        "doc_type": "voluntary_surrender",
        "date": "2026-08-01",
        # reason отсутствует
    }
    form = DocumentForm(data=data)
    assert not form.is_valid()
    assert "Для протокола явки с повинной укажите причину." in form.errors.get("reason", [])


@pytest.mark.django_db
def test_document_form_specific_requirements_satisfied():
    """
    Проверяем, что когда все специфические требования для типа документа выполнены,
    форма валидна (и общая проверка тоже проходит).
    """
    participant = Participant.objects.create(full_name="Петров П.П.")
    data_explanation = {
        "title": "Объяснение Петрова",
        "doc_type": "explanation",
        "date": "2026-08-01",
        "participant": participant.pk,
    }
    form_exp = DocumentForm(data=data_explanation)
    assert form_exp.is_valid()

    data_inspection = {
        "title": "Осмотр места",
        "doc_type": "inspection_protokol",
        "date": "2026-08-01",
        "location": "г. Москва, ул. Пушкина, д. 10",
    }
    form_ins = DocumentForm(data=data_inspection)
    assert form_ins.is_valid()

    data_orm = {
        "title": "ОРМ поручение",
        "doc_type": "orm_instruction",
        "date": "2026-08-01",
        "target_action": "Провести опрос свидетелей",
    }
    form_orm = DocumentForm(data=data_orm)
    assert form_orm.is_valid()

    data_surrender = {
        "title": "Явка с повинной Сидорова",
        "doc_type": "voluntary_surrender",
        "date": "2026-08-01",
        "reason": "Сознался в совершении преступления",
    }
    form_sur = DocumentForm(data=data_surrender)
    assert form_sur.is_valid()