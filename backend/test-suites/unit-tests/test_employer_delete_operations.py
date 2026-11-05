from uuid import uuid4

from scout.persistence.employer_repository import EmployerRepository


class Cursor:
    rowcount = 1


class ConnectionDouble:
    def __init__(self):
        self.statements = []

    def execute(self, query, params):
        self.statements.append((query, params))
        return Cursor()


def test_company_delete_removes_runs_vacancies_sources_then_employer():
    connection = ConnectionDouble()
    employer_id = uuid4()

    deleted = EmployerRepository(connection).delete(employer_id)

    assert deleted is True
    assert len(connection.statements) == 4
    assert "DELETE FROM extraction_runs" in connection.statements[0][0]
    assert "DELETE FROM vacancies" in connection.statements[1][0]
    assert "DELETE FROM employer_sources" in connection.statements[2][0]
    assert "DELETE FROM employers" in connection.statements[3][0]
    assert all(params == (employer_id,) for _, params in connection.statements)
