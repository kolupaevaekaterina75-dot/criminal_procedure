import io
from pathlib import Path
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

import pytest
from django.test import TestCase
from django.utils import timezone

from documents.docx_constructor import (
    get_template_path,
    generate_docx_from_document,
)
from documents.models import Document, DocumentType, Participant


class TestGetTemplatePath(TestCase):
    def test_known_doc_type_returns_path(self):
        path = get_template_path("explanation")
        assert path.name == "explanation.docx"
        assert isinstance(path, Path)
        # Интеграционная проверка: файл должен реально существовать
        assert path.exists(), f"Шаблон не найден: {path}"

    def test_unknown_doc_type_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            get_template_path("unknown_type_that_does_not_exist_in_folder")

    def test_namespace_input_works(self):
        ns = SimpleNamespace(code="explanation")
        path = get_template_path(ns)
        expected_path = Path(__file__).resolve().parent.parent / "docx_templates" / "explanation.docx"
        assert str(path) == str(expected_path.resolve())
        assert path.exists(), f"Шаблон не найден по пути: {path}"


class TestGenerateDocxFromDocumentUnit(TestCase):
    @patch("documents.docx_constructor.get_template_path")
    @patch("docxtpl.DocxTemplate")
    def test_basic_render_and_bytes_returned(self, mock_tpl_class, mock_get_template):
        mock_tpl_instance = MagicMock()
        mock_tpl_class.return_value = mock_tpl_instance

        def fake_save(buffer: io.BytesIO):
            buffer.write(b"fake-docx-bytes-content")

        mock_tpl_instance.save.side_effect = fake_save
        mock_tpl_instance.render.return_value = None

        # Возвращаем любой валидный Path — главное, чтобы он был объектом Path
        mock_get_template.return_value = Path("/fake/path/to/template.docx")

        doc_type = DocumentType(code="explanation", name="Объяснение")
        doc = SimpleNamespace(
            doc_type=doc_type,
            title="Test Title",
            created_at=timezone.now(),
            issue_date=timezone.now().date(),
            location="Moscow",
            case_number="123",
            content_text="Тестовый текст",
            investigator=None,
        )

        docx_bytes = generate_docx_from_document(doc)

        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0
        mock_get_template.assert_called_once_with(doc_type)
        mock_tpl_class.assert_called_once_with("/fake/path/to/template.docx")
        mock_tpl_instance.render.assert_called_once()
        mock_tpl_instance.save.assert_called_once()


class TestIntegrationWithRealDocumentModel(TestCase):
    """
    Интеграционный тест: реально использует шаблон и создаёт корректные объекты в БД.
    Цель — проверить, что generate_docx_from_document работает с настоящими моделями.
    """

    @classmethod
    def setUpTestData(cls):
        # Создаём тип документа
        cls.doc_type = DocumentType.objects.create(code="explanation", name="Объяснение")

        # Создаём участника-следователя (Participant), который будет investigator
        cls.investigator = Participant.objects.create(
            full_name="Иванов И.И.",
            role="следователь",
            position="Следователь",
            department="Следственный отдел",
        )

    def test_integration_with_real_document(self):
        document = Document.objects.create(
            title="Интеграционный тест",
            doc_type=self.doc_type,
            status="ready",
            created_at=timezone.now(),
            case_date=timezone.now().date(),
            case_number="67890",
            issue_date=timezone.now().date(),
            location="Москва",
            content_text="Тестовый контент документа",
            investigator=self.investigator,  # Обязательно: FK не NULL
        )

        # Проверяем, что шаблон реально существует (иначе тест сразу падает с понятной ошибкой)
        template_path = get_template_path(document.doc_type)
        assert template_path.exists(), f"Шаблон не найден для теста: {template_path}"

        docx_bytes = generate_docx_from_document(document)

        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0