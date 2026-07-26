from django import forms
from .models import Document, Participant

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "title", "doc_type", "date", "location",
            "participant", "start_time", "end_time",
            # добавь сюда специфичные поля, если они есть в модели и нужны в шаблонах:
            "object_description", "items_found", "target_action", "deadline", "reason"
        ]

    def clean(self):
        cleaned_data = super().clean()

        title = cleaned_data.get("title")
        doc_type = cleaned_data.get("doc_type")
        date = cleaned_data.get("date")

        if not title or not doc_type or not date:
            raise forms.ValidationError("Обязательно заполните название документа, тип и дату.")

        # Валидация по типу документа
        if doc_type == "explanation" and not cleaned_data.get("participant"):
            self.add_error("participant", "Для объяснения обязательно укажите участника.")

        if doc_type == "inspection_protokol" and not cleaned_data.get("location"):
            self.add_error("location", "Для протокола осмотра места происшествия обязательно укажите место.")

        if doc_type == "orm_instruction" and not cleaned_data.get("target_action"):
            self.add_error("target_action", "Для поручения укажите целевое действие.")

        if doc_type == "voluntary_surrender" and not cleaned_data.get("reason"):
            self.add_error("reason", "Для протокола явки с повинной укажите причину.")

        return cleaned_data