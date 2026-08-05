import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase
from datetime import date, timedelta

from documents.models import Participant, DocumentType, Document, STATUS_CHOICES, ROLE_COLORS


class TestParticipant(TestCase):
    def test_str_representation(self):
        p = Participant.objects.create(
            full_name="Иванов Иван Иванович",
            role="suspect",
            side="prosecution",
            birth_date=date.today(),
            birth_place="Москва",
            address="ул. Ленина, 1",
            phone="79990000000",
            citizenship="РФ",
            education="Высшее",
            marital_status="Женат",
            employment="ООО Ромашка",
            work_phone="74950000000",
            military_duty="Не служил",
            criminal_record="Нет",
            document_type="Паспорт",
            document_number="123456",
            signature="Иванов",
        )
        assert str(p) == "Иванов Иван Иванович (Подозреваемый)"

    def test_get_background_color_valid_role(self):
        p = Participant(role="suspect")
        assert p.get_background_color() == ROLE_COLORS["suspect"]

    def test_get_background_color_unknown_role_default(self):
        # роль, которой нет в ROLE_COLORS
        p = Participant(role="fake_role")
        assert p.get_background_color() == "#FFFFFF"

    def test_register_by_phone_creates_new_participant(self):
        phone = "+79990000001"
        full_name = "Иванов Иван Иванович"
        birth_date = timezone.datetime(1995, 3, 10).date()

        obj, created = Participant.register_by_phone(phone, birth_date=birth_date, full_name=full_name)

        assert created is True
        assert obj.phone == phone
        assert obj.full_name == full_name
        assert obj.birth_date == birth_date

    def test_register_by_phone_does_not_update_full_name_on_existing(self):
        original_phone = "+79990000002"
        original_full_name = "Старый Участник"
        original_birth_date = timezone.datetime(1980, 5, 20).date()

        original = Participant.objects.create(
            phone=original_phone,
            full_name=original_full_name,
            birth_date=original_birth_date,
        )

        new_full_name = "Новый Участник"

        obj, created = Participant.register_by_phone(original_phone, full_name=new_full_name)

        assert created is False
        assert obj.pk == original.pk
        assert obj.phone == original_phone

        # get_or_create НЕ обновляет существующие поля, поэтому full_name остаётся старым
        obj.refresh_from_db()
        assert obj.full_name == original_full_name

    def test_register_by_phone_raises_validation_error_on_empty_phone(self):
        with pytest.raises(ValidationError):
            Participant.register_by_phone("")

        with pytest.raises(ValidationError):
            Participant.register_by_phone("   ")

    def test_register_by_phone_uses_explicit_birth_date(self):
        phone = "+79990000003"
        birth_date = timezone.datetime(2000, 7, 7).date()

        obj, created = Participant.register_by_phone(phone, birth_date=birth_date)

        assert created is True
        assert obj.birth_date == birth_date

    def test_assign_status_updates_role_and_side(self):
        p = Participant.objects.create(
            full_name="Сидоров Сидор Сидорович",
            role="other",
            side="other",
            birth_date=date.today(),
            birth_place="Город",
            address="Улица",
            phone="79003334455",
            citizenship="РФ",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )
        p.assign_status(role="witness", side="prosecution")
        p.refresh_from_db()
        assert p.role == "witness"
        assert p.side == "prosecution"

    def test_assign_status_raises_validation_on_invalid_role(self):
        p = Participant.objects.create(
            full_name="Тест",
            role="other",
            side="other",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="70000000000",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )
        with pytest.raises(ValidationError) as exc_info:
            p.assign_status(role="invalid_role")
        error_dict = exc_info.value.error_dict
        assert "role" in error_dict

    def test_assign_status_raises_validation_on_invalid_side(self):
        p = Participant.objects.create(
            full_name="Тест2",
            role="other",
            side="other",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="71111111111",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )
        with pytest.raises(ValidationError) as exc_info:
            p.assign_status(side="invalid_side")
        error_dict = exc_info.value.error_dict
        assert "side" in error_dict


class TestDocumentType(TestCase):
    def test_str_representation(self):
        dt = DocumentType.objects.create(code="protocol_interrogation", name="Протокол допроса")
        assert str(dt) == "Протокол допроса"


class TestDocument(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_type = DocumentType.objects.create(code="inspection_protokol", name="Протокол осмотра")

        # Используем только Participant с нужными ролями
        cls.main_participant = Participant.objects.create(
            full_name="Основной участник",
            role="other",
            side="other",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="70000000000",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )

        cls.witness1 = Participant.objects.create(
            full_name="Понятой 1",
            role="witness",
            side="other",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="71111111111",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )

        cls.witness2 = Participant.objects.create(
            full_name="Понятой 2",
            role="witness",
            side="other",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="72222222222",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )

        cls.investigator = Participant.objects.create(
            full_name="Следователь Иванов",
            role="investigator",
            side="prosecution",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="73333333333",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )

        cls.specialist = Participant.objects.create(
            full_name="Специалист Петров",
            role="expert",
            side="other",
            birth_date=date.today(),
            birth_place="-",
            address="-",
            phone="74444444444",
            citizenship="-",
            education="-",
            marital_status="-",
            employment="-",
            work_phone="-",
            military_duty="-",
            criminal_record="-",
            document_type="-",
            document_number="-",
            signature="-",
        )

    def test_str_representation(self):
        doc = Document.objects.create(
            reason="Основание",
            case_date=date.today(),
            case_number="123",
            article_uk_rf="105 УК РФ",
            doc_type=self.doc_type,
            participant=self.main_participant,
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            investigator=self.investigator,
            specialist=self.specialist,
        )
        expected = f"{self.doc_type.name} №123 от {date.today()}"
        assert str(doc) == expected

    def test_clean_valid_dates(self):
        # case_date <= issue_date — всё ок
        doc = Document(
            reason="Основание",
            case_date=date.today() - timedelta(days=1),
            issue_date=date.today(),
            doc_type=self.doc_type,
            participant=self.main_participant,
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            investigator=self.investigator,
            specialist=self.specialist,
        )
        # clean() не выбрасывает ошибок
        doc.clean()

    def test_clean_raises_when_issue_date_earlier_than_case_date(self):
        doc = Document(
            reason="Основание",
            case_date=date.today(),
            issue_date=date.today() - timedelta(days=1),  # раньше
            doc_type=self.doc_type,
            participant=self.main_participant,
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            investigator=self.investigator,
            specialist=self.specialist,
        )
        with pytest.raises(ValidationError) as exc_info:
            doc.clean()
        error_dict = exc_info.value.error_dict
        assert "issue_date" in error_dict

    def test_default_issue_date_is_today(self):
        doc = Document.objects.create(
            reason="Основание",
            case_date=date.today(),
            case_number="456",
            article_uk_rf="228 УК РФ",
            doc_type=self.doc_type,
            participant=self.main_participant,
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            investigator=self.investigator,
            specialist=self.specialist,
        )
        assert doc.issue_date == date.today()