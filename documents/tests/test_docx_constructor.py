import io
import os
import tempfile
import zipfile
from pathlib import Path

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
        doc_type = DocumentType.objects.create(
            code="inspection_protokol",
            name="Протокол осмотра места происшествия",
        )
        path = get_template_path(doc_type.code)
        assert isinstance(path, Path)
        assert path.name == "inspection_protokol.docx"

    def test_unknown_doc_type_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            get_template_path("UNKNOWN_TYPE_123")


class TestGenerateDocxFromDocumentUnit(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_type = DocumentType.objects.create(
            code="inspection_protokol",
            name="Протокол осмотра места происшествия",
        )
        cls.investigator = Participant.objects.create(
            full_name="Иванов И.И.",
            role="investigator",
            side="state",
            birth_date=timezone.now().date(),
        )

    def test_basic_render_and_bytes_returned(self):
        doc = Document.objects.create(
            title="Протокол осмотра",
            doc_type=self.doc_type,
            case_date=timezone.now().date(),
            case_number="123456",
            article_uk_rf="105 УК РФ",
            issue_date=timezone.now().date(),
            investigator=self.investigator,
            location="ул. Ленина, д. 1",
            place="Место осмотра",
        )

        result_bytes = generate_docx_from_document(doc)
        assert isinstance(result_bytes, bytes)
        assert len(result_bytes) > 0

        # Создаём временный файл, записываем байты, закрываем его, потом читаем через zipfile
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp.write(result_bytes)
                tmp_path = tmp.name

            # Файл уже закрыт — можно безопасно открывать zipfile
            with zipfile.ZipFile(tmp_path) as z:
                namelist = z.namelist()
                assert "word/document.xml" in namelist
                assert "[Content_Types].xml" in namelist
        finally:
            # Удаляем временный файл, если он был создан
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestIntegrationWithRealDocumentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_type = DocumentType.objects.create(
            code="explanation",
            name="Объяснение",
        )
        cls.investigator = Participant.objects.create(
            full_name="Петров П.П.",
            role="investigator",
            side="state",
            birth_date=timezone.now().date(),
        )
        cls.participant = Participant.objects.create(
            full_name="Сидоров С.С.",
            role="suspect",
            side="defense",
            birth_date=timezone.now().date(),
        )

    def test_integration_with_real_document(self):
        doc = Document.objects.create(
            title="Объяснение подозреваемого",
            doc_type=self.doc_type,
            case_date=timezone.now().date(),
            case_number="654321",
            article_uk_rf="228 УК РФ",
            issue_date=timezone.now().date(),
            investigator=self.investigator,
            participant=self.participant,
            reason="Сознался в совершении преступления",
        )

        result = generate_docx_from_document(doc)
        assert isinstance(result, bytes)
        assert len(result) > 0