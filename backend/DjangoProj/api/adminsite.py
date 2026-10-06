from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class CustomAdminSite(AdminSite):
    site_header = 'Кадровый портал — администрирование'
    site_title = 'Кадровый портал'
    index_title = 'Разделы сайта'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        api_app = next((a for a in app_list if a['app_label'] == 'api'), None)
        if not api_app:
            return app_list

        all_models = api_app['models']

        # Группы повторяют структуру сайта: «Главная», «Наша команда», «Карьера», «Нет коррупции!», «Информация»
        groups = {
            'Главная страница': {
                'app_label': 'main_page_group',
                'models': ['NewsPost', 'WorkPartner'],
            },
            'Наша команда: структура администрации': {
                'app_label': 'admin_structure_group',
                'models': ['Department', 'Deputy'],
            },
            'Наша команда: доска почёта': {
                'app_label': 'honorboard_group',
                'models': ['HonorBoardStaffMember'],
            },
            'Наша команда: контакты': {
                'app_label': 'staff_group',
                'models': ['ContactStaffMember', 'Branch'],
            },
            'Карьера: вакансии': {
                'app_label': 'vacancies_group',
                'models': ['Vacancy', 'VacancyDocument', 'JobApplication', 'VacancySubscription',
                           'RequiredExperience', 'JobType', 'WorkingHours'],
            },
            'Карьера: конкурсы': {
                'app_label': 'tenders_group',
                'models': ['Competition', 'CompetitionResult', 'CompetitionDocument', 'Tender'],
            },
            'Карьера: кадровый резерв': {
                'app_label': 'staff_reserve_group',
                'models': ['StaffReserveInfo', 'StaffReservePosition', 'StaffReserveDocument'],
            },
            'Карьера: молодёжь': {
                'app_label': 'youth_group',
                'models': ['YouthInfo', 'PracticeApplication'],
            },
            'Карьера: профразвитие': {
                'app_label': 'profdev_group',
                'models': ['TrainingEvent', 'TrainingFeedback'],
            },
            'Нет коррупции!: основная информация': {
                'app_label': 'anticorruption_group',
                'models': ['AntiCorruptionInfo', 'AntiCorruptionDocumentCategory', 'AntiCorruptionDocument', 'CorruptionReport'],
            },
            'Нет коррупции!: просвещение': {
                'app_label': 'anticorruption_education_group',
                'models': ['EducationReviewPage', 'EducationPosition', 'EducationCategory', 'EducationLegalAct'],
            },
            'Информация: обратная связь': {
                'app_label': 'feedback_group',
                'models': ['Feedback'],
            },
            'Настройки': {
                'app_label': 'settings_group',
                'models': ['ApplicationRecipient', 'BranchesGlobal'],
            },
            'Пользователи': {
                'app_label': 'users_group',
                'models': ['User', 'Group'],
                'superuser_only': True,
            },
        }

        auth_app = next((a for a in app_list if a['app_label'] == 'auth'), None)
        auth_models = auth_app['models'] if auth_app else []

        new_app_list = []
        for name, config in groups.items():
            if config.get('superuser_only') and not request.user.is_superuser:
                continue

            if config['app_label'] == 'users_group':
                group_models = [
                    m for m in auth_models
                    if m['object_name'] in config['models']
                ]
            else:
                group_models = [
                    m for m in all_models
                    if m['object_name'] in config['models']
                ]

            # Порядок внутри группы — как в списке models (главное сверху), а не по алфавиту
            group_models.sort(key=lambda m: config['models'].index(m['object_name']))

            if group_models:
                new_app_list.append({
                    'name': name,
                    'app_label': config['app_label'],
                    'models': group_models,
                })

        return new_app_list


custom_admin_site = CustomAdminSite(name='custom_admin')
