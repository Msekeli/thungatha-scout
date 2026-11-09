from scout.persistence.vacancy_collection_read_operations import (
    VacancyCollectionReadOperations,
)
from scout.persistence.vacancy_detail_read_operations import (
    VacancyDetailReadOperations,
)
from scout.persistence.vacancy_export_read_operations import (
    VacancyExportReadOperations,
)
from scout.persistence.vacancy_metrics_read_operations import (
    VacancyMetricsReadOperations,
)
from scout.persistence.vacancy_page_read_operations import VacancyPageReadOperations


class VacancyReadOperations(
    VacancyMetricsReadOperations,
    VacancyPageReadOperations,
    VacancyCollectionReadOperations,
    VacancyDetailReadOperations,
    VacancyExportReadOperations,
):
    pass
