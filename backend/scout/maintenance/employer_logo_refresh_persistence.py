from scout.persistence.database_connection import get_database_connection


def load_employers():
    with get_database_connection() as connection:
        return connection.execute(
            """SELECT e.id, e.name, e.website_url, e.logo_url,
                      (SELECT es.employer_careers_url FROM employer_sources es
                       WHERE es.employer_id = e.id
                       AND es.employer_careers_url IS NOT NULL
                       ORDER BY es.created_at DESC LIMIT 1) AS careers_url,
                      (SELECT json_agg(es.source_url ORDER BY es.created_at DESC)
                       FROM employer_sources es WHERE es.employer_id = e.id
                       AND es.source_url IS NOT NULL) AS source_urls
               FROM employers e ORDER BY e.name"""
        ).fetchall()


def persist_logo(employer, logo_url, source_url, logo_type) -> bool:
    with get_database_connection() as connection, connection.transaction():
        saved = connection.execute(
            """UPDATE employers
               SET logo_url = %s, logo_source_url = %s, logo_type = %s,
                   updated_at = NOW()
               WHERE id = %s AND logo_url IS NOT DISTINCT FROM %s
               RETURNING id""",
            (logo_url, source_url, logo_type, employer["id"], employer["logo_url"]),
        ).fetchone()
    return bool(saved)
