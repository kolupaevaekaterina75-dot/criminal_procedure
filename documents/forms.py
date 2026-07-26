from django import forms
from .models import Document, Participant

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        # перечисли все поля, которые должны быть в форме
        fields = [
            'title', 'doc_type', 'date', 'location',
            'participant', 'content_notes',
        ]

    def clean(self):
        cleaned_data = super().clean()

        # Пример валидации: проверяем, что ключевые поля не пустые
        title = cleaned_data.get('title')
        doc_type = cleaned_data.get('doc_type')
        date = cleaned_data.get('date')

        if not title or not doc_type or not date:
            raise forms.ValidationError(
                "Обязательно заполните название документа, тип и дату."
            )

        # Для «объяснения» обязательно нужен participant
        if doc_type == 'explanation' and not cleaned_data.get('participant'):
            self.add_error(
                'participant',
                "Для объяснения обязательно укажите участника."
            )

        return cleaned_data