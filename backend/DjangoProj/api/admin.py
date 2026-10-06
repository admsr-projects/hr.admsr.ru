from django.db.models import Q
from django.contrib import admin
from .forms import DepartmentAdminForm, VacancyAdminForm
from .widgets import MarkdownFieldsMixin
from .models import (
    Tender, ContactStaffMember, HonorBoardStaffMember, Vacancy, JobApplication, Branch,
    RequiredExperience, JobType, WorkingHours, AntiCorruptionDocument,
    AntiCorruptionDocumentCategory, AntiCorruptionInfo, CorruptionReport, BranchesGlobal, Feedback, VacancySubscription,
    Competition, CompetitionResult, StaffReserveInfo, StaffReservePosition, StaffReserveDocument, VacancyDocument, WorkPartner, YouthInfo,
    PracticeApplication, TrainingEvent, TrainingFeedback, NewsPost, Department, Deputy,
    DeputyDepartment, ApplicationRecipient, CompetitionDocument, CompetitionWinner,
    EducationReviewPage, EducationCategory, EducationLegalAct, EducationPosition,
)
from .adminsite import custom_admin_site
from .admin_auth import register_auth_models


STAFF_MEMBER_FORM_FIELDS = [
    'surname', 'name', 'patronym', 'role', 'branch',
    'phone', 'email', 'cabinet_number', 'description', 'image',
    'order', 'is_active', 'is_management_head', 'show_on_reserve',
]


class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name', 'address']


class TenderAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'show_on_main_page', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active', 'show_on_main_page']


class ContactStaffMemberAdmin(admin.ModelAdmin):
    list_display = [
        'surname', 'name', 'role', 'branch', 'cabinet_number', 'phone',
        'order', 'is_active', 'is_management_head', 'show_on_reserve',
    ]
    list_filter = ['is_active', 'is_management_head', 'show_on_reserve', 'branch']
    search_fields = ['name', 'surname', 'patronym', 'role', 'phone', 'email']
    list_editable = ['order', 'is_active', 'is_management_head', 'show_on_reserve']
    fields = STAFF_MEMBER_FORM_FIELDS

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(Q(show_on_contacts=True) | Q(is_management_head=True))

    def save_model(self, request, obj, form, change):
        obj.show_on_contacts = True
        if not change:
            obj.show_on_honorboard = False
        super().save_model(request, obj, form, change)


class HonorBoardStaffMemberAdmin(admin.ModelAdmin):
    list_display = [
        'surname', 'name', 'role', 'branch', 'order', 'is_active', 'show_on_reserve',
    ]
    list_filter = ['is_active', 'show_on_reserve', 'branch']
    search_fields = ['name', 'surname', 'patronym', 'role', 'description']
    list_editable = ['order', 'is_active', 'show_on_reserve']
    fields = STAFF_MEMBER_FORM_FIELDS

    def get_queryset(self, request):
        return super().get_queryset(request).filter(show_on_honorboard=True)

    def save_model(self, request, obj, form, change):
        obj.show_on_honorboard = True
        if not change:
            obj.show_on_contacts = False
        super().save_model(request, obj, form, change)


class VacancyAdmin(admin.ModelAdmin):
    form = VacancyAdminForm
    list_display = ['title', 'branch', 'location', 'salary', 'required_experience', 'job_type', 'is_active', 'published_at']
    list_filter = ['is_active', 'required_experience', 'job_type', 'published_at']
    search_fields = ['title', 'branch']
    list_editable = ['is_active']
    date_hierarchy = 'published_at'
    fieldsets = [
        ('Основное', {'fields': ['title', 'branch', 'location', 'salary', 'published_at']}),
        ('Детали', {'fields': ['experience', 'required_experience', 'job_type', 'working_hours', 'is_active']}),
        ('Описание и навыки', {'fields': ['description', 'skills']}),
    ]


class RequiredExperienceAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class JobTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'vacancy_title', 'email', 'phone', 'created_at']
    list_filter = ['vacancy_title', 'created_at', 'marital_status']
    search_fields = ['last_name', 'first_name', 'email', 'phone']
    readonly_fields = ['consent_false_info', 'consent_verification', 'consent_personal_data', 'consent_resume_forwarding']


class AntiCorruptionDocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['tab_label', 'slug', 'order']
    list_editable = ['order']
    search_fields = ['tab_label', 'slug', 'title']
    ordering = ['order', 'tab_label']


class AntiCorruptionDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name']
    ordering = ['category__order', '-created_at']
    autocomplete_fields = ['category']


class AntiCorruptionInfoAdmin(MarkdownFieldsMixin, admin.ModelAdmin):
    markdown_fields = ('intro',)
    list_display = ['__str__', 'updated_at']
    fields = ['intro', 'work_schedule', 'address', 'officials', 'esia_feedback_url']


class EducationReviewPageAdmin(MarkdownFieldsMixin, admin.ModelAdmin):
    markdown_fields = ('intro',)
    list_display = ['__str__', 'updated_at']
    fields = ['eyebrow', 'title', 'lead', 'approved_note', 'period', 'intro', 'source_note']

    def has_add_permission(self, request):
        return not EducationReviewPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class EducationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'color', 'order']
    list_editable = ['order']
    search_fields = ['name', 'short_name']


class EducationLegalActAdmin(admin.ModelAdmin):
    list_display = ['abbr', 'full_name', 'has_changed_note']
    search_fields = ['abbr', 'full_name']

    @admin.display(boolean=True, description='Помечен как изменённый')
    def has_changed_note(self, obj):
        return bool(obj.changed_note)


class EducationPositionAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'category', 'outcome', 'municipal', 'is_published']
    list_display_links = ['number', 'title']
    list_filter = ['category', 'outcome', 'municipal', 'norm_changed', 'in_favor_of_official', 'is_published']
    list_editable = ['is_published']
    search_fields = ['title', 'key_quote', 'facts_summary', 'legal_basis', 'subjects']
    ordering = ['number']
    fieldsets = [
        (None, {'fields': ['number', 'is_published', 'title', 'category']}),
        ('Правовая позиция', {'fields': ['key_quote', 'facts_summary', 'lesson']}),
        ('Участники и нормы', {'fields': ['subjects', 'legal_basis', 'municipal', 'norm_changed']}),
        ('Исход', {'fields': ['outcome', 'outcome_note', 'in_favor_of_official', 'amount']}),
        ('Хронология', {'fields': ['year', 'years', 'page']}),
        ('Полный текст', {'fields': ['full_text', 'notes']}),
    ]


class CorruptionReportAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['full_name', 'email']


class BranchesGlobalAdmin(admin.ModelAdmin):
    list_display = ['name', 'link']
    search_fields = ['name']


class WorkPartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'url']
    fields = ['name', 'url', 'logo_file', 'logo_path', 'order', 'is_active']


class VacancySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'branch_display', 'has_resume', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'branch', 'desired_position']
    list_editable = ['is_active']
    readonly_fields = ['created_at']
    fields = [
        'name', 'email', 'branch', 'is_active', 'created_at',
        'resume', 'phone', 'desired_position', 'education', 'work_experience', 'about',
    ]

    @admin.display(description='Резюме', boolean=True)
    def has_resume(self, obj):
        return bool(obj.resume or obj.desired_position or obj.education or obj.work_experience or obj.about)

    @admin.display(description='Отраслевой функциональный орган')
    def branch_display(self, obj):
        return obj.branch.strip() if obj.branch else 'Любой ОФО / не имеет значения'


class CompetitionAdmin(MarkdownFieldsMixin, admin.ModelAdmin):
    markdown_fields = ('content', 'requirements', 'acceptance_info')
    list_display = ['title', 'competition_type', 'date_start', 'date_end', 'is_active', 'created_at']
    list_filter = ['is_active', 'competition_type', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_active']


class CompetitionDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'competition_type', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['competition_type', 'is_active']
    search_fields = ['name']
    fields = ['name', 'competition_type', 'file', 'order', 'is_active']


class CompetitionWinnerInline(admin.StackedInline):
    model = CompetitionWinner
    extra = 1
    fields = ['full_name', 'position', 'description', 'photo', 'order']


class ApplicationRecipientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'is_active', 'receives_vacancies',
        'receives_reserve', 'receives_practice', 'receives_training', 'receives_feedback',
    ]
    list_editable = [
        'is_active', 'receives_vacancies', 'receives_reserve',
        'receives_practice', 'receives_training', 'receives_feedback',
    ]
    list_filter = ['is_active']
    search_fields = ['full_name', 'email']


class CompetitionResultAdmin(admin.ModelAdmin):
    list_display = ['title', 'competition_type', 'completed_at', 'created_at']
    list_editable = ['competition_type']
    list_filter = ['competition_type', 'completed_at', 'created_at']
    search_fields = ['title']
    fields = ['title', 'competition_type', 'decree_conduct', 'decree_results', 'completed_at']
    inlines = [CompetitionWinnerInline]


class StaffReserveInfoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'updated_at']
    fields = ['purpose', 'additional_content']


class StaffReservePositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    fields = ['title', 'description', 'order', 'is_active']


class StaffReserveDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    fields = ['name', 'file', 'order', 'is_active']


class VacancyDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    fields = ['name', 'file', 'order', 'is_active']


class YouthInfoAdmin(MarkdownFieldsMixin, admin.ModelAdmin):
    markdown_fields = ('intro',)
    list_display = ['__str__', 'updated_at']
    fields = [
        'intro', 'practice_institutions', 'practice_steps',
        'internship_content', 'school_content',
    ]


class PracticeApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'educational_institution', 'course',
        'practice_period', 'created_at',
    ]
    list_filter = ['created_at', 'educational_institution']
    search_fields = ['last_name', 'first_name', 'email', 'educational_institution']
    readonly_fields = ['consent_personal_data', 'created_at']


class TrainingEventAdmin(MarkdownFieldsMixin, admin.ModelAdmin):
    markdown_fields = ('description',)
    list_display = ['title', 'event_type', 'event_date', 'location', 'is_published', 'created_at']
    list_filter = ['event_type', 'is_published', 'event_date']
    search_fields = ['title', 'description', 'location']
    list_editable = ['is_published']
    date_hierarchy = 'event_date'


class TrainingFeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'department', 'message']
    readonly_fields = ['created_at']


class NewsPostAdmin(MarkdownFieldsMixin, admin.ModelAdmin):
    markdown_fields = ('content',)
    list_display = ['title', 'published_at', 'is_published', 'show_on_main', 'order', 'created_at']
    list_filter = ['is_published', 'show_on_main', 'published_at']
    search_fields = ['title', 'description']
    list_editable = ['is_published', 'show_on_main', 'order']
    date_hierarchy = 'published_at'


class DepartmentAdmin(admin.ModelAdmin):
    form = DepartmentAdminForm
    list_display = ['name', 'slug', 'vacancy_branch', 'is_published', 'order', 'updated_at']
    list_filter = ['is_published']
    search_fields = ['name', 'slug', 'vacancy_branch']
    list_editable = ['is_published', 'order']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = [
        ('Основное', {'fields': ['slug', 'name', 'intro', 'image', 'is_published', 'order']}),
        ('О деятельности', {'fields': ['about_paragraphs', 'units', 'tasks']}),
        ('Руководитель', {'fields': ['head_name', 'head_role', 'head_phone', 'head_email']}),
        ('Контакты', {'fields': ['phone', 'email', 'vacancy_branch']}),
    ]


class DeputyDepartmentInline(admin.TabularInline):
    model = DeputyDepartment
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['department']


class DeputyAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'patronymic', 'role', 'is_published', 'order']
    list_filter = ['is_published']
    search_fields = ['surname', 'name', 'patronymic', 'role']
    list_editable = ['is_published', 'order']
    inlines = [DeputyDepartmentInline]
    fieldsets = [
        ('Основное', {'fields': ['role', 'surname', 'name', 'patronymic', 'image', 'is_published', 'order']}),
    ]


custom_admin_site.register(Branch, BranchAdmin)
custom_admin_site.register(Tender, TenderAdmin)
custom_admin_site.register(ContactStaffMember, ContactStaffMemberAdmin)
custom_admin_site.register(HonorBoardStaffMember, HonorBoardStaffMemberAdmin)
custom_admin_site.register(Vacancy, VacancyAdmin)
custom_admin_site.register(RequiredExperience, RequiredExperienceAdmin)
custom_admin_site.register(JobType, JobTypeAdmin)
custom_admin_site.register(WorkingHours, WorkingHoursAdmin)
custom_admin_site.register(JobApplication, JobApplicationAdmin)
custom_admin_site.register(AntiCorruptionDocumentCategory, AntiCorruptionDocumentCategoryAdmin)
custom_admin_site.register(AntiCorruptionDocument, AntiCorruptionDocumentAdmin)
custom_admin_site.register(AntiCorruptionInfo, AntiCorruptionInfoAdmin)
custom_admin_site.register(EducationReviewPage, EducationReviewPageAdmin)
custom_admin_site.register(EducationPosition, EducationPositionAdmin)
custom_admin_site.register(EducationCategory, EducationCategoryAdmin)
custom_admin_site.register(EducationLegalAct, EducationLegalActAdmin)
custom_admin_site.register(CorruptionReport, CorruptionReportAdmin)
custom_admin_site.register(BranchesGlobal, BranchesGlobalAdmin)
custom_admin_site.register(WorkPartner, WorkPartnerAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message']

custom_admin_site.register(Feedback, FeedbackAdmin)
custom_admin_site.register(VacancySubscription, VacancySubscriptionAdmin)
custom_admin_site.register(Competition, CompetitionAdmin)
custom_admin_site.register(CompetitionResult, CompetitionResultAdmin)
custom_admin_site.register(CompetitionDocument, CompetitionDocumentAdmin)
custom_admin_site.register(ApplicationRecipient, ApplicationRecipientAdmin)
custom_admin_site.register(StaffReserveInfo, StaffReserveInfoAdmin)
custom_admin_site.register(StaffReservePosition, StaffReservePositionAdmin)
custom_admin_site.register(StaffReserveDocument, StaffReserveDocumentAdmin)
custom_admin_site.register(VacancyDocument, VacancyDocumentAdmin)
custom_admin_site.register(YouthInfo, YouthInfoAdmin)
custom_admin_site.register(PracticeApplication, PracticeApplicationAdmin)
custom_admin_site.register(TrainingEvent, TrainingEventAdmin)
custom_admin_site.register(TrainingFeedback, TrainingFeedbackAdmin)
custom_admin_site.register(NewsPost, NewsPostAdmin)
custom_admin_site.register(Department, DepartmentAdmin)
custom_admin_site.register(Deputy, DeputyAdmin)

register_auth_models(custom_admin_site)
