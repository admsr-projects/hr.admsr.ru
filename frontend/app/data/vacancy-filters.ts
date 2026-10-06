/** Значение «Все» в селектах фильтра вакансий */
export const VACANCY_FILTER_ALL = 'all'

export interface VacancyFilterState {
  q: string
  branch: string
  required_experience: string
  job_type: string
}

export function emptyVacancyFilters(): VacancyFilterState {
  return {
    q: '',
    branch: VACANCY_FILTER_ALL,
    required_experience: VACANCY_FILTER_ALL,
    job_type: VACANCY_FILTER_ALL,
  }
}
