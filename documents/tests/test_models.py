import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase
from datetime import date, timedelta

from documents.models import (
    Participant,
    DocumentType,
    Employee,
    Witness,
    Specialist,
    Document,
    STATUS_CHOICES,
    ROLE_COLORS,
)


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
        phone = "+79991234567"
        obj, created = Participant.register_by_phone(
        phone=phone,
        birth_date=date(1995, 3, 10),
        first_name="Иван",
        last_name="Иванов",
        )
        self.assertTrue(created)
        self.assertEqual(obj.phone, phone)
        self.assertEqual(obj.birth_date, date(1995, 3, 10))

    def test_register_by_phone_updates_existing_participant(self):
        from datetime import date
        phone = "+79991112233"
        original, _ = Participant.objects.get_or_create(
            phone=phone,
            defaults={
                "first_name": "Пётр",
                "last_name": "Петров",
                "birth_date": date(1980, 5, 20),
            },
        )
        updated, created = Participant.register_by_phone(
            phone=phone,
            birth_date=date(1980, 5, 20),  # та же дата
            first_name="Пётр",
            last_name="Петров-Новый",      # меняем фамилию
        )

        self.assertFalse(created)          # существующий, не создаётся заново
        self.assertEqual(updated.pk, original.pk)
        self.assertEqual(updated.last_name, "Петров-Новый")

    def test_register_by_phone_raises_validation_error_on_empty_phone(self):
        with pytest.raises(ValidationError) as exc_info:
            Participant.register_by_phone(
                full_name="ФИО",
                phone="",
                role="other",
                side="other",
            )
        error_dict = exc_info.value.error_dict
        assert "phone" in error_dict

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


class TestEmployee(TestCase):
    def test_str_representation(self):
        e = Employee.objects.create(full_name="Следователь Иванов", position="Следователь", rank="Майор")
        assert str(e) == "Следователь Иванов"


class TestWitness(TestCase):
    def test_str_representation(self):
        w = Witness.objects.create(full_name="Понятой Петров", address="Адрес", phone="70000000000")
        assert str(w) == "Понятой Петров"


class TestSpecialist(TestCase):
    def test_str_representation(self):
        s = Specialist.objects.create(
            full_name="Эксперт Сидоров",
            position="Судебный эксперт",
            organization="Экспертное бюро",
            status="draft",
        )
        assert str(s) == "Эксперт Сидоров (Судебный эксперт)"


class TestDocument(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_type = DocumentType.objects.create(code="inspection_protocol", name="Протокол осмотра")
        cls.participant = Participant.objects.create(
            full_name="Участник",
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
        cls.employee = Employee.objects.create(full_name="Составитель", position="Должность")
        cls.witness1 = Witness.objects.create(full_name="Понятой 1", address="Адрес 1")
        cls.witness2 = Witness.objects.create(full_name="Понятой 2", address="Адрес 2")
        cls.specialist = Specialist.objects.create(
            full_name="Специалист",
            position="Позиция",
            organization="Организация",
            status="draft",
        )

    def test_str_representation(self):
        doc = Document.objects.create(
            reason="Основание",
            case_date=date.today(),
            case_number="123",
            article_uk_rf="105 УК РФ",
            doc_type=self.doc_type,
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            author=self.employee,
            investigator=self.employee,
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
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            author=self.employee,
            investigator=self.employee,
        )
        # clean() не выбрасывает ошибок
        doc.clean()

    def test_clean_raises_when_issue_date_earlier_than_case_date(self):
        doc = Document(
            reason="Основание",
            case_date=date.today(),
            issue_date=date.today() - timedelta(days=1),  # раньше
            doc_type=self.doc_type,
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            author=self.employee,
            investigator=self.employee,
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
            witness1=self.witness1,
            witness2=self.witness2,
            creator_full_name="ФИО составителя",
            recipient_position="Должность получателя",
            information_source="Источник",
            location="Место составления",
            place="Место проведения",
            authority_name="Орган",
            recorded_correctly="Соответствует",
            author=self.employee,
            investigator=self.employee,
        )
        assert doc.issue_date == date.today()