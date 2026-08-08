from django import forms
from .models import Document, Participant, DocumentType

class DocumentForm(forms.ModelForm):
    # Явно делаем title обязательным, даже если в модели blank=True
    title = forms.CharField(required=True, max_length=255)

    class Meta:
        model = Document
        fields = [
            'title',
            'doc_type',
            'case_number',
            'case_date',
            'issue_date',
            'participant',
            'status',
            'content',
            'location',
            'target_action',
            'reason',
        ]

    def clean(self):
        cleaned_data = super().clean()
        doc_type_obj = cleaned_data.get('doc_type')

        # Если тип документа не выбран, дальше проверять нет смысла
        if not doc_type_obj:
            return cleaned_data

        code = doc_type_obj.code

        # Специфичные проверки по типу документа
        if code == 'explanation' and not cleaned_data.get('participant'):
            self.add_error('participant', 'Для объяснения обязательно указать участника')

        if code == 'inspection_protokol' and not cleaned_data.get('location'):
            self.add_error('location', 'Для протокола осмотра обязательно указать место')

        if code == 'orm_instruction' and not cleaned_data.get('target_action'):
            self.add_error('target_action', 'Для поручения ОРМ обязательно указать действие')

        if code == 'voluntary_surrender' and not cleaned_data.get('reason'):
            self.add_error('reason', 'Для явки с повинной обязательно указать причину')

        return cleaned_data
