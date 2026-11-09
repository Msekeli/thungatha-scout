from typing import Any

from psycopg.connection import Connection


def import_employer(
    item: dict[str, Any],
    connection: Connection,
    counts: dict[str, int],
) -> dict[str, Any]:
    employer = connection.execute(
        """
        SELECT id, website_url FROM employers
        WHERE name = %s ORDER BY created_at, id LIMIT 1
        """,
        (item["name"],),
    ).fetchone()
    careers_url = item.get("website_url") or item.get("careers_url")
    existing_url = (employer.get("website_url") or "").strip() if employer else ""
    if existing_url and careers_url and existing_url != careers_url:
        raise ValueError(f"Employer name already exists with another website: {item['name']}")
    if employer is not None:
        if not existing_url and careers_url:
            updated = connection.execute(
                """
                UPDATE employers SET website_url = %s, updated_at = NOW()
                WHERE id = %s RETURNING id, website_url
                """,
                (careers_url, employer["id"]),
            ).fetchone()
            if updated:
                counts["employers_updated"] += 1
                return updated
        return employer

    employer = connection.execute(
        """
        INSERT INTO employers (name, website_url, organization_type)
        VALUES (%s, %s, %s)
        RETURNING id, website_url
        """,
        (item["name"], careers_url, item.get("organization_classification", "unresolved")),
    ).fetchone()
    counts["employers_created"] += 1
    return employer
