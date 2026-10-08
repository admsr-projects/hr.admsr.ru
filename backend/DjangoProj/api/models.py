from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Tender(models.Model):
    CATEGORY_CHOICES = [
        ('info', 'Информация'),
        ('results', 'Результаты'),
        ('rules', 'Положения и правила'),
    ]

    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField('Название', max_length=255)
    link = models.FileField('Файл', upload_to='tenders/')
    is_active = models.BooleanField('Активен', default=True, help_text='Неактивные документы не публикуются на сайте')
    show_on_main_page = models.BooleanField('Показывать на главной странице конкурсов', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Документ раздела «Конкурсы»'
        verbose_name_plural = 'Документы раздела «Конкурсы»'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_category_display()}] {self.name}'


class Branch(models.Model):
    name = models.CharField('Название', max_length=255)
    address = models.CharField('Адрес', max_length=255)

    class Meta:
        verbose_name = 'Отдел (для контактов)'
        verbose_name_plural = 'Отделы (для контактов)'

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    name = models.CharField('Имя', max_length=255, blank=True)
    surname = models.CharField('Фамилия', max_length=255, blank=True)
    patronym = models.CharField('Отчество', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    cabinet_number = models.CharField('Номер кабинета', max_length=50, blank=True)
    role = models.CharField('Должность', max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Отдел')
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Фото', upload_to='staff/', blank=True, null=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    show_on_honorboard = models.BooleanField('Показывать на доске почёта', default=True)
    show_on_contacts = models.BooleanField('Показывать в контактах', default=False)
    is_management_head = models.BooleanField('Начальник управления (блок на странице контактов)', default=False)
    show_on_reserve = models.BooleanField('Показывать в кадровом резерве', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['order']

    def clean(self):
        if self.is_active and self.show_on_reserve:
            raise ValidationError(
                'Сотрудник не может быть одновременно активным и в кадровом резерве'
            )
        if self.is_management_head:
            others = StaffMember.objects.filter(is_management_head=True)
            if self.pk:
                others = others.exclude(pk=self.pk)
            if others.exists():
                raise ValidationError(
                    'Начальником управления может быть только один сотрудник'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronym or ""}'.strip()


class ContactStaffMember(StaffMember):
    """Сотрудники для справочника контактов (proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Сотрудник (контакты)'
        verbose_name_plural = 'Сотрудники (контакты)'


class HonorBoardStaffMember(StaffMember):
    """Лауреаты доски почёта (proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Лауреат доски почёта'
        verbose_name_plural = 'Лауреаты доски почёта'


class WorkSchedule(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'

    def __str__(self):
        return self.name


class RequiredExperience(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'Требуемый опыт'
        verbose_name_plural = 'Требуемый опыт'

    def __str__(self):
        return self.name


class JobType(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'Тип должности'
        verbose_name_plural = 'Типы должностей'

    def __str__(self):
        return self.name


class WorkingHours(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'Режим работы'
        verbose_name_plural = 'Режимы работы'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    title = models.CharField('Название', max_length=255) 
    branch = models.CharField(
        'Подразделение',
        max_length=255,
        blank=True,
        help_text='Отраслевой (функциональный) орган из утверждённого списка',
    ) 
    location = models.CharField('Локация', max_length=255) 
    salary = models.CharField('Оплата труда', max_length=255, blank=True, help_text='Необязательно: если поле пустое, оплата в карточке и на странице вакансии не показывается')
    employment_type = models.CharField('Тип занятости', max_length=100, blank=True) 
    experience = models.CharField('Опыт', max_length=100, blank=True) 
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='График работы')
    required_experience = models.ForeignKey(RequiredExperience, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Требуемый опыт')
    job_type = models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Тип должности')
    is_new = models.BooleanField('Новая вакансия', default=False) 
    description = models.TextField('Описание', blank=True)
    skills = models.TextField('Навыки', blank=True, help_text='Каждый навык с новой строки') 
    working_hours = models.ForeignKey(WorkingHours, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Режим работы')
    is_active = models.BooleanField('Активна', default=True)
    published_at = models.DateField('Дата публикации', default=timezone.localdate)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    subscribers_notified_at = models.DateTimeField(
        'Подписчики уведомлены',
        null=True,
        blank=True,
        editable=False,
        help_text='Когда подписчикам ушло письмо о вакансии. Пока пусто, письмо уйдёт при первой публикации (активной вакансии).',
    )

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title


class BranchesGlobal(models.Model):
    name = models.CharField('Название', max_length=255)
    link = models.CharField('Ссылка', max_length=500)

    class Meta:
        verbose_name = 'Отдел Администрации'
        verbose_name_plural = 'Все отделы Администрации'
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkPartner(models.Model):
    name = models.CharField('Название', max_length=255)
    url = models.CharField('Ссылка', max_length=500)
    logo_file = models.ImageField(
        'Логотип (файл)',
        upload_to='partners/logos/',
        blank=True,
        null=True,
        help_text='Загрузите PNG, SVG или JPG. Имеет приоритет над путём к статичному файлу.',
    )
    logo_path = models.CharField(
        'Логотип (путь на сайте)',
        max_length=500,
        blank=True,
        help_text='Например /Icons/i-custom-fss.svg — используется, если файл не загружен.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать на главной', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Партнёр'
        verbose_name_plural = 'С нами работают'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class AntiCorruptionDocumentCategory(models.Model):
    slug = models.SlugField('Код вкладки', max_length=50, unique=True)
    tab_label = models.CharField('Название вкладки', max_length=120)
    title = models.CharField('Полное название категории', max_length=255)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория антикоррупционных документов'
        verbose_name_plural = 'Категории антикоррупционных документов'
        ordering = ['order', 'tab_label']

    def __str__(self):
        return self.tab_label


class AntiCorruptionDocument(models.Model):
    category = models.ForeignKey(
        AntiCorruptionDocumentCategory,
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name='Категория',
    )
    name = models.CharField('Название', max_length=255)
    file = models.FileField('Файл', upload_to='anti_corruption_docs/')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Антикоррупционный документ'
        verbose_name_plural = 'Антикоррупционные документы'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.category}] {self.name}'


class AntiCorruptionInfo(models.Model):
    intro = models.TextField(
        'Вводный текст',
        blank=True,
        default='Федеральный закон от 25.12.2008 № 273-ФЗ «О противодействии коррупции» устанавливает '
                'правовые и организационные основы предупреждения и борьбы с коррупцией.',
    )
    work_schedule = models.TextField(
        'График работы УМСКН',
        blank=True,
        default='Понедельник – четверг: 8:30 – 17:30\n'
                'Пятница: 8:30 – 16:15\n'
                'Перерыв: 13:00 – 13:45',
    )
    address = models.TextField(
        'Адрес',
        blank=True,
        default='628408, Ханты-Мансийский автономный округ — Югра, '
                'г. Сургут, ул. 30 лет Победы, д. 45/2',
    )
    officials = models.TextField(
        'Ответственные должностные лица',
        blank=True,
        help_text='Каждый сотрудник с новой строки: ФИО, должность, телефон',
    )
    esia_feedback_url = models.URLField(
        'Ссылка на Платформу обратной связи (ЕСИА)',
        blank=True,
        default='https://pos.gosuslugi.ru/landing/',
    )
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Страница «Нет коррупции!»'
        verbose_name_plural = 'Страница «Нет коррупции!»'

    def __str__(self):
        return 'Нет коррупции!'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class EducationReviewPage(models.Model):
    """Страница «Антикоррупционное просвещение»: заголовок и вводные тексты обзора."""

    eyebrow = models.CharField(
        'Надзаголовок',
        max_length=255,
        default='Тематический обзор Верховного Суда РФ N 14/2026',
    )
    title = models.CharField(
        'Заголовок обзора',
        max_length=255,
        default='27 правовых позиций по антикоррупционным делам',
    )
    lead = models.TextField(
        'Краткое описание',
        blank=True,
        help_text='Абзац под заголовком обзора.',
    )
    approved_note = models.TextField(
        'Реквизиты утверждения',
        blank=True,
        help_text='Например: «Утверждён постановлением Президиума ВС РФ от 01.07.2026 N 17А/2026».',
    )
    period = models.CharField(
        'Период изученной практики',
        max_length=50,
        blank=True,
        default='2020–2026',
        help_text='Показывается в блоке цифр.',
    )
    intro = models.TextField(
        'Вводная часть обзора',
        blank=True,
    )
    source_note = models.TextField(
        'Источник',
        blank=True,
        help_text='Пояснение внизу страницы: откуда взят материал и какую силу имеет.',
    )
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Страница «Антикоррупционное просвещение»'
        verbose_name_plural = 'Страница «Антикоррупционное просвещение»'

    def __str__(self):
        return 'Антикоррупционное просвещение'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class EducationCategory(models.Model):
    COLOR_CHOICES = [
        ('indigo', 'Индиго'),
        ('violet', 'Фиолетовый'),
        ('teal', 'Бирюзовый'),
        ('emerald', 'Зелёный'),
        ('amber', 'Янтарный'),
        ('slate', 'Серый'),
    ]

    name = models.CharField('Название', max_length=255)
    short_name = models.CharField('Короткое название', max_length=120, help_text='Для меток и диаграмм.')
    color = models.CharField('Цвет', max_length=20, choices=COLOR_CHOICES, default='indigo')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория правовых позиций'
        verbose_name_plural = 'Категории правовых позиций'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class EducationLegalAct(models.Model):
    abbr = models.CharField(
        'Сокращение',
        max_length=50,
        unique=True,
        help_text='Как в нормах позиций, например «ФЗ-273» или «ГК РФ». '
                  'Норма «ст. 12 ФЗ-273» автоматически относится к акту «ФЗ-273».',
    )
    full_name = models.TextField('Полное название')
    changed_note = models.TextField(
        'Примечание об изменении',
        blank=True,
        help_text='Если акт утратил силу или изменён — на странице появится пометка «Норма изменена».',
    )

    class Meta:
        verbose_name = 'Нормативный акт'
        verbose_name_plural = 'Нормативные акты'
        ordering = ['abbr']

    def __str__(self):
        return self.abbr


class EducationPosition(models.Model):
    OUTCOME_CHOICES = [
        ('granted', 'Удовлетворено'),
        ('granted_partly', 'Удовлетворено частично'),
        ('lawful', 'Признано правомерным'),
        ('denied', 'Отказано'),
        ('remanded', 'Направлено на новое рассмотрение'),
        ('motion_rejected', 'Ходатайство отклонено'),
    ]

    number = models.PositiveSmallIntegerField(
        'Номер позиции',
        unique=True,
        help_text='Номер используется в ссылках и на карточках; по нему же сортируются позиции.',
    )
    is_published = models.BooleanField('Показывать на сайте', default=True)
    title = models.CharField('Заголовок', max_length=255)
    category = models.ForeignKey(
        EducationCategory,
        on_delete=models.PROTECT,
        related_name='positions',
        verbose_name='Категория',
    )
    subjects = models.TextField('Кто фигурирует', blank=True, help_text='Каждый субъект с новой строки.')
    legal_basis = models.TextField(
        'Применённые нормы',
        blank=True,
        help_text='Каждая норма с новой строки, например «ст. 15 ФЗ-25». Нормативный акт определяется по сокращению в конце.',
    )
    outcome = models.CharField('Исход', max_length=20, choices=OUTCOME_CHOICES, blank=True)
    outcome_note = models.CharField('Пояснение к исходу', max_length=255, blank=True)
    in_favor_of_official = models.BooleanField('Решено в пользу служащего / ответчика', default=False)
    municipal = models.BooleanField('Касается муниципального уровня', default=False)
    norm_changed = models.BooleanField('Норма изменена', default=False)
    key_quote = models.TextField('Правовая позиция (дословно)')
    facts_summary = models.TextField('Фабула дела', blank=True)
    lesson = models.TextField('Что важно служащему', blank=True)
    page = models.PositiveSmallIntegerField('Страница в PDF', null=True, blank=True)
    year = models.PositiveSmallIntegerField(
        'Год на таймлайне',
        null=True,
        blank=True,
        help_text='Последний год событий из фабулы. Без года позиция попадёт в колонку «Без дат в фабуле».',
    )
    years = models.CharField('Период в фабуле', max_length=50, blank=True, help_text='Например «2020–2023».')
    amount = models.PositiveBigIntegerField(
        'Сумма, обращённая в доход РФ, ₽',
        null=True,
        blank=True,
        help_text='Только если обзор называет сумму.',
    )
    full_text = models.TextField(
        'Полный текст позиции',
        blank=True,
        help_text='Абзацы разделяются пустой строкой. Знак сноски в тексте — «<1>».',
    )
    notes = models.TextField(
        'Сноски',
        blank=True,
        help_text='Каждая сноска с новой строки в виде «1. Текст сноски».',
    )

    class Meta:
        verbose_name = 'Правовая позиция'
        verbose_name_plural = 'Правовые позиции'
        ordering = ['number']

    def __str__(self):
        return f'№ {self.number}. {self.title}'


class JobApplication(models.Model):
    MARITAL_STATUS_CHOICES = [
        ('single', 'Холост/Не замужем'),
        ('married', 'Женат/Замужем'),
        ('divorced', 'Разведен(а)'),
        ('widowed', 'Вдовец/Вдова'),
    ]

    vacancy_title = models.CharField('Вакансия', max_length=255, blank=True)
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    birth_date = models.DateField('Дата рождения')
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    registration_address = models.TextField('Адрес прописки')
    residence_address = models.TextField('Адрес проживания')
    citizenship = models.CharField('Гражданство', max_length=100)
    education = models.CharField('Образование', max_length=255)
    specialty = models.CharField('Специальность', max_length=255)
    municipal_experience = models.CharField('Стаж муниципальной службы', max_length=255, blank=True)
    work_experience = models.TextField('Трудовая деятельность', blank=True)
    marital_status = models.CharField('Семейное положение', max_length=20, choices=MARITAL_STATUS_CHOICES)
    children = models.CharField('Наличие детей', max_length=255, blank=True)
    photo = models.FileField('Фото', upload_to='photos/', blank=True, null=True)
    resume = models.FileField('Резюме', upload_to='resumes/')
    vacancy_source = models.TextField('Откуда узнал(а)', blank=True)
    created_at = models.DateTimeField('Дата подачи', auto_now_add=True)

    # Required consent checkboxes (applicant must check all before submitting)
    consent_false_info = models.BooleanField(
        'Согласие с последствиями ложных сведений',
        default=False
        
    )
    consent_verification = models.BooleanField(
        'Согласие на проверочные мероприятия',
        default=False
    )
    consent_personal_data = models.BooleanField(
        'Согласие на обработку персональных данных (152-ФЗ)',
        default=False
    )
    consent_resume_forwarding = models.BooleanField(
        'Согласие на направление анкеты в поселения и организации района',
        default=False
    )

    class Meta:
        verbose_name = 'Заявка на вакансию'
        verbose_name_plural = 'Заявки на вакансии'

    def __str__(self):
        return f'{self.last_name} {self.first_name} — {self.vacancy_title or "без вакансии"}'


class Feedback(models.Model):
    message = models.TextField('Сообщение')
    photo = models.ImageField('Фото', upload_to='feedback_photos/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['-created_at']

    def __str__(self):
        return f'Обратная связь ({self.created_at.strftime("%d.%m.%Y %H:%M")})'


class VacancySubscription(models.Model):
    name = models.CharField('Имя', max_length=150, blank=True)
    email = models.EmailField('Email')
    branch = models.CharField('Отраслевой функциональный орган', max_length=255, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата подписки', auto_now_add=True)

    # Резюме (необязательно): файлом или заполненное в электронной форме
    resume = models.FileField('Файл резюме', upload_to='subscription_resumes/', blank=True, null=True)
    phone = models.CharField('Телефон', max_length=30, blank=True)
    desired_position = models.CharField('Желаемая должность', max_length=255, blank=True)
    education = models.CharField('Образование', max_length=255, blank=True)
    work_experience = models.TextField('Опыт работы', blank=True)
    about = models.TextField('О себе, навыки', blank=True)

    class Meta:
        verbose_name = 'Подписка на вакансии'
        verbose_name_plural = 'Подписки на вакансии'
        ordering = ['-created_at']

    def __str__(self):
        who = self.name.strip() if self.name else self.email
        ofo = self.branch.strip() if self.branch else 'любой ОФО'
        return f'{who} — {ofo} ({self.created_at.strftime("%d.%m.%Y")})'


class Competition(models.Model):
    TYPE_VACANCY = 'vacancy'
    TYPE_RESERVE = 'reserve'
    TYPE_CHOICES = [
        (TYPE_VACANCY, 'На замещение вакантной должности'),
        (TYPE_RESERVE, 'На формирование кадрового резерва'),
    ]

    title = models.CharField('Название', max_length=255)
    competition_type = models.CharField('Тип конкурса', max_length=20, choices=TYPE_CHOICES, default=TYPE_VACANCY)
    content = models.TextField('Содержание (веб-контент)', blank=True)
    date_start = models.DateField('Дата начала приёма документов', null=True, blank=True)
    date_end = models.DateField('Дата окончания приёма документов', null=True, blank=True)
    requirements = models.TextField('Требования', blank=True)
    acceptance_info = models.TextField('Место и время приёма документов', blank=True)
    contact_phones = models.CharField('Телефоны ответственных лиц', max_length=500, blank=True)
    is_active = models.BooleanField('Действующий конкурс', default=True)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'
        ordering = ['-date_end', '-created_at']

    def __str__(self):
        return self.title


class CompetitionDocument(models.Model):
    """Нормативные документы, регламентирующие порядок проведения конкурсов."""
    name = models.CharField('Название', max_length=255)
    competition_type = models.CharField(
        'Для конкурсов',
        max_length=20,
        choices=Competition.TYPE_CHOICES,
        default=Competition.TYPE_RESERVE,
    )
    file = models.FileField('Файл', upload_to='competitions/documents/')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Нормативный документ конкурсов'
        verbose_name_plural = 'Нормативные документы конкурсов'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class CompetitionResult(models.Model):
    title = models.CharField('Название', max_length=255)
    competition_type = models.CharField(
        'Тип результата',
        max_length=20,
        choices=Competition.TYPE_CHOICES,
        default=Competition.TYPE_VACANCY,
    )
    decree_conduct = models.FileField('Постановление о проведении конкурса', upload_to='competitions/conduct/')
    decree_results = models.FileField('Постановление о результатах конкурса', upload_to='competitions/results/')
    completed_at = models.DateField('Дата завершения', null=True, blank=True)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Результат конкурса'
        verbose_name_plural = 'Результаты конкурсов'
        ordering = ['-completed_at', '-created_at']

    def __str__(self):
        return self.title


class CompetitionWinner(models.Model):
    """Победитель конкурса — отдельное информационное окно в результатах."""
    result = models.ForeignKey(
        CompetitionResult,
        on_delete=models.CASCADE,
        related_name='winners',
        verbose_name='Результат конкурса',
    )
    full_name = models.CharField('ФИО', max_length=255)
    position = models.CharField('Должность / орган', max_length=500, blank=True)
    description = models.TextField('Информация', blank=True)
    photo = models.ImageField('Фото', upload_to='competitions/winners/', blank=True, null=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Победитель конкурса'
        verbose_name_plural = 'Победители конкурса'
        ordering = ['order', 'id']

    def __str__(self):
        return self.full_name


class StaffReserveInfo(models.Model):
    purpose = models.TextField(
        'Цель формирования кадрового резерва',
        blank=True,
        default='Формирование кадрового резерва направлено на обеспечение администрации '
                'Сургутского района квалифицированными кадрами для замещения вакантных должностей.',
    )
    positions = models.TextField(
        'Должности, на которые формируется резерв',
        blank=True,
        help_text='Каждая должность с новой строки',
    )
    additional_content = models.TextField('Дополнительная информация', blank=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Страница «Кадровый резерв»'
        verbose_name_plural = 'Страница «Кадровый резерв»'

    def __str__(self):
        return 'Информация о кадровом резерве'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class StaffReservePosition(models.Model):
    title = models.CharField('Должность', max_length=255)
    description = models.TextField(
        'Описание',
        help_text='Кратко: зона ответственности и требования к кандидату в резерв на эту должность',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать на сайте', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Должность кадрового резерва'
        verbose_name_plural = 'Должности кадрового резерва'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class StaffReserveDocument(models.Model):
    name = models.CharField('Название', max_length=255)
    file = models.FileField('Файл', upload_to='staff_reserve/documents/')
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Неактивные документы не публикуются на сайте',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Документ кадрового резерва'
        verbose_name_plural = 'Документы кадрового резерва'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class VacancyDocument(models.Model):
    name = models.CharField('Название', max_length=255)
    file = models.FileField('Файл', upload_to='vacancies/documents/')
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Неактивные документы не публикуются на сайте',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Документ раздела «Вакансии»'
        verbose_name_plural = 'Документы раздела «Вакансии»'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class YouthInfo(models.Model):
    intro = models.TextField(
        'Вводный текст',
        blank=True,
        default='Раздел предназначен для популяризации муниципальной службы и ранней профориентации.',
    )
    practice_institutions = models.TextField(
        'Учебные заведения (соглашения)',
        blank=True,
        help_text='Каждое учебное заведение с новой строки',
    )
    practice_steps = models.TextField(
        'Этапы: как попасть на практику в АСР',
        blank=True,
        default='1. Определитесь, в каком отраслевом функциональном органе вы хотите проходить практику. '
                'Со структурой администрации можно ознакомиться в разделе [«О нас»](/about#admin-structure).\n'
                '2. Согласуйте прохождение практики с учебным заведением.\n'
                '3. Заполните и отправьте заявку на практику через форму на этой странице.\n'
                '4. Дождитесь ответа специалиста управления муниципальной службы, кадров и наград.',
    )
    internship_content = models.TextField(
        'Стажировка',
        blank=True,
        default='Информация о стажировках будет размещена дополнительно.',
    )
    school_content = models.TextField(
        'Школьникам',
        blank=True,
        default='Информация для школьников будет размещена дополнительно.',
    )
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Страница «Муниципальная служба для молодёжи»'
        verbose_name_plural = 'Страница «Муниципальная служба для молодёжи»'

    def __str__(self):
        return 'Муниципальная служба для молодёжи'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PracticeApplication(models.Model):
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    birth_date = models.DateField('Дата рождения')
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    educational_institution = models.CharField('Учебное заведение', max_length=255)
    course = models.CharField('Курс', max_length=50)
    specialty = models.CharField('Специальность', max_length=255)
    practice_period = models.CharField('Желаемый период практики', max_length=255)
    preferred_department = models.CharField('Желаемый орган', max_length=255, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    application_letter = models.FileField(
        'Сопроводительное письмо',
        upload_to='practice_applications/',
        blank=True,
        null=True,
    )
    consent_personal_data = models.BooleanField(
        'Согласие на обработку персональных данных (152-ФЗ)',
        default=False,
    )
    created_at = models.DateTimeField('Дата подачи', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на практику'
        verbose_name_plural = 'Заявки на практику'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.last_name} {self.first_name} — {self.educational_institution}'


class TrainingEvent(models.Model):
    TYPE_TRAINING = 'training'
    TYPE_LEADERSHIP = 'leadership'
    TYPE_MASTERCLASS = 'masterclass'
    TYPE_BEST_PRACTICE = 'best_practice'
    TYPE_CHOICES = [
        (TYPE_TRAINING, 'Обучающее мероприятие'),
        (TYPE_LEADERSHIP, 'Встреча с руководством'),
        (TYPE_MASTERCLASS, 'Мастер-класс'),
        (TYPE_BEST_PRACTICE, 'Лучшая практика'),
    ]

    title = models.CharField('Название', max_length=255)
    event_type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default=TYPE_TRAINING)
    description = models.TextField('Описание', blank=True)
    event_date = models.DateTimeField('Дата и время')
    location = models.CharField('Место проведения', max_length=255, blank=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['event_date']

    def __str__(self):
        return f'{self.title} ({self.event_date.strftime("%d.%m.%Y")})'


class TrainingFeedback(models.Model):
    name = models.CharField('Имя', max_length=150, blank=True)
    department = models.CharField('Подразделение', max_length=255, blank=True)
    message = models.TextField('Предложение')
    created_at = models.DateTimeField('Дата отправки', auto_now_add=True)

    class Meta:
        verbose_name = 'Предложение по обучению'
        verbose_name_plural = 'Предложения по обучению'
        ordering = ['-created_at']

    def __str__(self):
        label = self.name or 'Анонимно'
        return f'{label} ({self.created_at.strftime("%d.%m.%Y %H:%M")})'


class ApplicationRecipient(models.Model):
    """Уполномоченные лица, на почту которых дублируются заявки с портала."""
    full_name = models.CharField('ФИО', max_length=255)
    email = models.EmailField('Email для рассылки заявок')
    is_active = models.BooleanField('Получает письма', default=True)
    receives_vacancies = models.BooleanField('Вакансии и подписка с резюме', default=True)
    receives_reserve = models.BooleanField('Кадровый резерв', default=True)
    receives_practice = models.BooleanField('Практика', default=True)
    receives_training = models.BooleanField('Обучение', default=True)
    receives_feedback = models.BooleanField('Обратная связь', default=False)

    class Meta:
        verbose_name = 'Получатель заявок'
        verbose_name_plural = 'Получатели заявок'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Department(models.Model):
    slug = models.SlugField('URL-идентификатор', max_length=100, unique=True)
    name = models.CharField('Название', max_length=500)
    intro = models.TextField(
        'Краткое описание',
        blank=True,
        default='Отраслевой (функциональный) орган администрации Сургутского района обеспечивает '
                'реализацию полномочий в своей сфере деятельности и взаимодействует с жителями района.',
    )
    about_paragraphs = models.TextField(
        'О деятельности',
        blank=True,
        help_text='Каждый абзац с новой строки',
    )
    units = models.TextField(
        'Структурные подразделения',
        blank=True,
        help_text='Каждое подразделение с новой строки',
    )
    tasks = models.TextField(
        'Задачи',
        blank=True,
        help_text='Каждая задача с новой строки',
    )
    head_name = models.CharField('Руководитель: ФИО', max_length=255, blank=True)
    head_role = models.CharField('Руководитель: должность', max_length=255, blank=True)
    head_phone = models.CharField('Руководитель: телефон', max_length=255, blank=True)
    head_email = models.EmailField('Руководитель: email', blank=True)
    phone = models.CharField('Телефон', max_length=255, blank=True)
    email = models.EmailField('Email', blank=True)
    image = models.ImageField('Фото', upload_to='departments/', blank=True, null=True)
    vacancy_branch = models.CharField(
        'Подразделение для вакансий',
        max_length=500,
        blank=True,
        help_text='ОФО из списка — должно совпадать с подразделением в вакансиях',
    )
    is_published = models.BooleanField('Опубликовано', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Орган администрации'
        verbose_name_plural = 'Органы администрации'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.vacancy_branch:
            self.vacancy_branch = self.name
        super().save(*args, **kwargs)


class Deputy(models.Model):
    role = models.CharField('Должность', max_length=255)
    surname = models.CharField('Фамилия', max_length=100)
    name = models.CharField('Имя', max_length=100)
    patronymic = models.CharField('Отчество', max_length=100)
    image = models.CharField(
        'Фото (URL или путь)',
        max_length=500,
        blank=True,
        help_text='Например: /images/people/markova.png',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликовано', default=True)
    departments = models.ManyToManyField(
        Department,
        through='DeputyDepartment',
        related_name='deputies',
        verbose_name='Органы',
    )

    class Meta:
        verbose_name = 'Заместитель главы'
        verbose_name_plural = 'Заместители главы'
        ordering = ['order', 'surname']

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'


class DeputyDepartment(models.Model):
    deputy = models.ForeignKey(
        Deputy,
        on_delete=models.CASCADE,
        related_name='deputy_departments',
        verbose_name='Заместитель',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='Орган',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Орган заместителя'
        verbose_name_plural = 'Органы заместителей'
        ordering = ['order']
        unique_together = [['deputy', 'department']]

    def __str__(self):
        return f'{self.deputy} — {self.department}'


class NewsPost(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Краткое описание')
    content = models.TextField('Полный текст', blank=True)
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    published_at = models.DateField('Дата публикации')
    is_published = models.BooleanField('Опубликовано', default=True)
    show_on_main = models.BooleanField('Показывать на главной', default=True)
    order = models.PositiveIntegerField('Порядок', default=0, help_text='Меньшее число — выше в списке')
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['order', '-published_at']

    def __str__(self):
        return self.title


class PersonalDataAccessLog(models.Model):
    """Журнал доступа к персональным данным: кто, когда и что смотрел, менял, скачивал, получил с сайта.

    Записи только добавляются (в админке журнал доступен лишь для чтения). Персональных данных
    субъектов в журнал не пишем: только тип записи, её номер и служебные сведения о действии.
    """
    ACTION_VIEW = 'view'
    ACTION_LIST = 'list'
    ACTION_ADD = 'add'
    ACTION_CHANGE = 'change'
    ACTION_DELETE = 'delete'
    ACTION_DOWNLOAD = 'download'
    ACTION_SUBMIT = 'submit'
    ACTION_TRANSFER = 'transfer'
    ACTION_LOGIN = 'login'
    ACTION_LOGIN_FAILED = 'login_failed'
    ACTION_LOGOUT = 'logout'
    ACTION_CHOICES = [
        (ACTION_VIEW, 'Просмотр записи'),
        (ACTION_LIST, 'Просмотр списка'),
        (ACTION_ADD, 'Создание записи'),
        (ACTION_CHANGE, 'Изменение записи'),
        (ACTION_DELETE, 'Удаление записи'),
        (ACTION_DOWNLOAD, 'Скачивание файла'),
        (ACTION_SUBMIT, 'Получено с сайта'),
        (ACTION_TRANSFER, 'Передача по почте'),
        (ACTION_LOGIN, 'Вход в админку'),
        (ACTION_LOGIN_FAILED, 'Неудачный вход'),
        (ACTION_LOGOUT, 'Выход из админки'),
    ]

    created_at = models.DateTimeField('Время', auto_now_add=True, db_index=True)
    action = models.CharField('Действие', max_length=20, choices=ACTION_CHOICES, db_index=True)
    user = models.ForeignKey(
        'auth.User', verbose_name='Пользователь', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    username = models.CharField('Логин', max_length=150, blank=True, db_index=True)
    object_type = models.CharField('Раздел / тип данных', max_length=120, blank=True)
    object_id = models.CharField('Номер записи', max_length=64, blank=True)
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user_agent = models.CharField('Браузер', max_length=255, blank=True)
    details = models.CharField('Подробности', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Запись журнала доступа к ПД'
        verbose_name_plural = 'Журнал доступа к ПД'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.created_at:%d.%m.%Y %H:%M:%S} {self.get_action_display()} — {self.username or "аноним"}'
