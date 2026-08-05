from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date


STATUS_CHOICES = [
    ('draft', _('Черновик')),
    ('ready', _('Готов к подписанию')),
    ('signed', _('Подписан')),
    ('sent', _('Направлен')),
    ('archived', _('В архиве')),
]

ROLE_COLORS = {
    'suspect': '#FFB6C1',      # розовый — подозреваемый
    'victim': '#90EE90',       # светло‑зелёный — потерпевший
    'witness': '#FFFACD',      # лимонный — свидетель/понятой
    'lawyer': '#ADD8E6',       # голубой — защитник (адвокат)
    'investigator': '#DCDCDC',  # светло‑серый — следователь
}


class Participant(models.Model):
    ROLE_CHOICES = [
        ('suspect', _('Подозреваемый')),
        ('OUR', _('Оперуполномоченный')),
        ('victim', _('Потерпевший')),
        ('witness', _('Понятой')),
        ('lawyer', _('Защитник (адвокат)')),
        ('investigator', _('Следователь')),
        ('UUP', _('Участковый уполномоченный')),
        ('expert', _('Эксперт')),
        ('other', _('Иное лицо')),
    ]

    SIDE_CHOICES = [
        ('prosecution', _('Сторона обвинения')),
        ('defense', _('Сторона защиты')),
        ('other', _('Иные лица')),
    ]

    full_name = models.CharField(
        max_length=255,
        verbose_name=_('ФИО'),
        db_index=True,
        # unique=False — убираем, чтобы не блокировать полных тёзок
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='other',
        verbose_name=_('Роль')
    )
    position = models.CharField(
        max_length=255,
        verbose_name=_('Должность / позиция'),
        blank=True,
        null=True,
    )
    side = models.CharField(
        max_length=50,
        choices=SIDE_CHOICES,
        default='other',
        verbose_name=_('Сторона')
    )

    birth_date = models.DateField(null=True, blank=True, verbose_name=_('Дата рождения'))
    birth_place = models.CharField(max_length=255, verbose_name=_('Место рождения'), blank=True)
    address = models.TextField(verbose_name=_('Адрес проживания'), blank=True)
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'), blank=True, db_index=True)

    citizenship = models.CharField(max_length=100, verbose_name=_('Гражданство'), blank=True)
    education = models.CharField(max_length=100, verbose_name=_('Образование'), blank=True)
    marital_status = models.CharField(max_length=50, verbose_name=_('Семейное положение'), blank=True)
    employment = models.CharField(max_length=255, verbose_name=_('Место работы/учёбы'), blank=True)
    work_phone = models.CharField(max_length=20, verbose_name=_('Рабочий телефон'), blank=True)
    military_duty = models.CharField(max_length=100, verbose_name=_('Отношение к воинской обязанности'), blank=True)
    criminal_record = models.TextField(verbose_name=_('Наличие судимости'), blank=True)
    document_type = models.CharField(max_length=100, verbose_name=_('Тип документа'), blank=True)
    document_number = models.CharField(max_length=20, verbose_name=_('Номер документа'), blank=True)
    signature = models.CharField(max_length=100, verbose_name=_('Подпись'), blank=True)

    created_at = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)

    class Meta:
        verbose_name = _('Участник уголовного дела')
        verbose_name_plural = _('Участники уголовного дела')
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    def get_background_color(self):
        """Возвращает цвет фона для роли участника (для шаблонов)."""
        return ROLE_COLORS.get(self.role, '#FFFFFF')

    @classmethod
    def register_by_phone(cls, phone: str, birth_date: date, **kwargs):
        if not phone or not phone.strip():
            raise ValidationError({'phone': _('Номер телефона обязателен')})

        phone = phone.strip()

        obj, created = cls.objects.get_or_create(
            phone=phone,
            defaults={
                'birth_date': birth_date,
                **kwargs,
            },
        )
        return obj, created

    def assign_status(self, role=None, side=None):
        role_dict = dict(self.ROLE_CHOICES)
        side_dict = dict(self.SIDE_CHOICES)

        errors = {}
        if role and role not in role_dict:
            errors['role'] = _('Недопустимая роль')
        if side and side not in side_dict:
            errors['side'] = _('Недопустимая сторона')

        if errors:
            raise ValidationError(errors)

        if role:
            self.role = role
        if side:
            self.side = side

        self.save(update_fields=['role', 'side', 'updated_at'] if hasattr(self, 'updated_at') else ['role', 'side'])

class Investigator(models.Model):  # <-- добавили эту модель
    name = models.CharField(max_length=255)
    badge_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
    
class DocumentType(models.Model):
    code = models.SlugField(
        _('Код'),
        unique=True,
        help_text=_('Например: explanation, inspection_protokol, voluntary_surrender, orm_instruction')
    )
    name = models.CharField(_('Название вида документа'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)

    class Meta:
        verbose_name = _('Вид документа')
        verbose_name_plural = _('Виды документов')
        ordering = ['name']

    def __str__(self):
        return self.name


def default_issue_date():
    return timezone.now().date()


class Document(models.Model):
    title = models.CharField(max_length=255, blank=False, verbose_name=_('Заголовок'))
    reason = models.TextField(verbose_name=_('Основание / причина'), blank=True)
    object_description = models.TextField(blank=True, null=True, verbose_name=_('Описание объекта'))
    target_action = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Целевое действие'))
    items_found = models.TextField(blank=True, null=True, verbose_name=_('Обнаруженные предметы'))
    deadline = models.DateField(null=True, blank=True, verbose_name=_('Срок исполнения'))
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    participant = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_as_main_participant',
        verbose_name=_('Основной участник')
    )

    doc_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        verbose_name=_('Вид документа')
    )

    case_date = models.DateField(_('Дата дела'))
    case_number = models.CharField(_('Номер уголовного дела'), max_length=100)
    article_uk_rf = models.CharField(_('Статья УК РФ'), max_length=100)

    witness1 = models.ForeignKey(
        Participant,
        related_name="documents_as_witness1",
        on_delete=models.PROTECT,
        verbose_name=_('Понятой 1'),
        null=True,
        blank=True
    )

    witness2 = models.ForeignKey(
        Participant,
        related_name="documents_as_witness2",
        on_delete=models.PROTECT,
        verbose_name=_('Понятой 2'),
        null=True,
        blank=True
    )

    # file_path убираем: вместо него лучше использовать FileField для реальных файлов
    # file_path = models.FilePathField(...)

    content = models.TextField(_('Содержание документа'), blank=True)
    issue_date = models.DateField(
        _('Дата составления документа'),
        default=default_issue_date
    )
    creator_full_name = models.CharField(_('ФИО составителя'), max_length=255, blank=True)
    recipient_position = models.CharField(_('Должность получателя'), max_length=255, blank=True)
    information_source = models.TextField(_('Источник получения информации'), blank=True)
    crime_description = models.TextField(_('Описание преступления'), blank=True)

    destination = models.CharField(_('Куда направляется'), max_length=255, blank=True)
    items_seized = models.TextField(_('Что изъято'), blank=True)
    statements = models.TextField(_('Заявления'), blank=True)
    tech_equipment = models.TextField(_('Техсредства'), blank=True)
    to_do = models.TextField(_('Что необходимо / выполнено'), blank=True)

    investigator = models.ForeignKey(
        Participant,
        on_delete=models.PROTECT,
        related_name="documents_authored",
        verbose_name=_('Следователь (автор)'),
        limit_choices_to={'role': 'investigator'}
    )

    location = models.CharField(_('Место составления'), max_length=255, blank=True)
    place = models.CharField(_('Место проведения'), max_length=255, blank=True)

    time = models.TimeField(_('Время'), null=True, blank=True)
    start_time = models.TimeField(_('Время начала'), null=True, blank=True)
    end_time = models.TimeField(_('Время окончания'), null=True, blank=True)

    authority_name = models.CharField(_('Наименование органа'), max_length=255, blank=True)
    recorded_correctly = models.CharField(_('Запись соответствует'), max_length=50, blank=True)

    investigation_circumstances = models.TextField(_('Обстоятельства расследования'), blank=True)
    required_actions = models.TextField(_('Необходимые действия'), blank=True)
    attachments = models.TextField(_('Приложения'), blank=True)

    message_from = models.CharField(_('От кого получено сообщение'), max_length=255, blank=True)
    message_about = models.TextField(_('О чем получено сообщение'), blank=True)
    arrived_to = models.CharField(_('Место прибытия'), max_length=255, blank=True)

    specialist = models.ForeignKey(
        Participant,
        on_delete=models.PROTECT,
        verbose_name=_('Специалист'),
        null=True,
        blank=True,
        limit_choices_to={'role': 'expert'},
        related_name="documents_as_specialist"
    )

    other_participants = models.TextField(_('Иные участвующие лица'), blank=True)

    weather_conditions = models.CharField(_('Погодные условия'), max_length=100, blank=True)
    lighting_conditions = models.CharField(_('Условия освещенности'), max_length=100, blank=True)
    technical_means = models.TextField(_('Технические средства'), blank=True)

    object_inspection = models.TextField(_('Объект осмотра'), blank=True)
    inspection_results = models.TextField(_('Результаты осмотра'), blank=True)
    examination_methods = models.TextField(_('Методы исследования'), blank=True)
    seized_items = models.TextField(_('Изъятые предметы'), blank=True)

    reading_method = models.CharField(_('Способ ознакомления'), max_length=100, blank=True)
    remarks = models.TextField(_('Замечания участников'), blank=True)

    witness1_signature = models.CharField(_('Подпись понятого 1'), max_length=50, blank=True)
    witness2_signature = models.CharField(_('Подпись понятого 2'), max_length=50, blank=True)
    specialist_signature = models.CharField(_('Подпись специалиста'), max_length=50, blank=True)
    other_participants_signatures = models.TextField(_('Подписи иных участников'), blank=True)
    investigator_signature = models.CharField(_('Подпись следователя'), max_length=50, blank=True)

    created_at = models.DateTimeField(_('Дата создания записи'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Уголовно‑процессуальный документ')
        verbose_name_plural = _('Уголовно‑процессуальные документы')
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.doc_type.name} №{self.case_number} от {self.issue_date}"

    def clean(self):
        super().clean()
        if self.case_date and self.issue_date:
            if self.case_date > self.issue_date:
                raise ValidationError({
                    'issue_date': _('Дата составления документа не может быть раньше даты дела')
                })

    def save(self, *args, **kwargs):
        # Автозаполнение issue_date, если не задано
        if not self.issue_date:
            self.issue_date = default_issue_date()
        super().save(*args, **kwargs)