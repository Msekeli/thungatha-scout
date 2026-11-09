from uuid import uuid4

from scout.ats_adapters.greenhouse_adapter.greenhouse_vacancy_mapper import map_greenhouse_job


def map_job(location, offices):
    return map_greenhouse_job(
        uuid4(),
        uuid4(),
        "https://boards.greenhouse.io/example/jobs/1",
        {
            "id": 1,
            "title": "Software Engineer",
            "absolute_url": "https://boards.greenhouse.io/example/jobs/1",
            "location": location,
            "offices": offices,
        },
        "fingerprint",
    )


def test_specific_office_overrides_broad_country_location():
    mapped = map_job(
        {"name": "South Africa"},
        [{"name": "Cape Town DC"}, {"name": "Cape Town Office"}],
    )
    assert mapped["location_text"] == "Cape Town"


def test_specific_office_overrides_broad_province_location():
    mapped = map_job(
        {"name": "Western Cape"},
        [{"name": "Cape Town Office"}],
    )
    assert mapped["location_text"] == "Cape Town"


def test_distinct_office_locations_are_preserved():
    mapped = map_job(
        {"name": "South Africa"},
        [{"name": "Cape Town DC"}, {"name": "Johannesburg DC"}],
    )
    assert mapped["location_text"] == "Cape Town | Johannesburg"


def test_specific_job_location_is_not_replaced_by_office_label():
    mapped = map_job(
        {"name": "Cape Town"},
        [{"name": "Cape Town Office"}],
    )
    assert mapped["location_text"] == "Cape Town"
