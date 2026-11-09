from uuid import uuid4


class FakeResult:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.row or []


class FakeConnection:
    def __init__(self):
        self.employers = []
        self.sources = []

    def execute(self, query, params=()):
        if "SELECT id, website_url FROM employers" in query:
            employer = next(
                (row for row in self.employers if row["name"] == params[0]),
                None,
            )
            return FakeResult(employer)
        if "UPDATE employers SET website_url" in query:
            employer = next(row for row in self.employers if row["id"] == params[1])
            employer["website_url"] = params[0]
            return FakeResult(employer)
        if "INSERT INTO employers" in query:
            employer = {
                "id": uuid4(), "name": params[0], "website_url": params[1],
                "location_evidence": params[3].obj,
            }
            self.employers.append(employer)
            return FakeResult(employer)
        if "SELECT id, employer_id, adapter_key" in query:
            source = next(
                (row for row in self.sources if row["normalized_url"] == params[0]),
                None,
            )
            return FakeResult(source)
        if "SELECT id, normalized_url" in query:
            matches = [
                row for row in self.sources
                if row["employer_id"] == params[0] and row["adapter_key"] == params[1]
            ]
            return FakeResult(matches)
        if "UPDATE employer_sources" in query:
            source_id = params[4]
            source = next(row for row in self.sources if row["id"] == source_id)
            source.update({
                "source_url": params[0], "employer_careers_url": params[1],
                "normalized_url": params[2] or source["normalized_url"],
                "adapter_config": params[3].obj,
            })
            return FakeResult(source)
        if "INSERT INTO employer_sources" in query:
            source = {
                "id": uuid4(), "employer_id": params[0], "adapter_key": params[1],
                "source_url": params[2], "employer_careers_url": params[3],
                "normalized_url": params[4], "adapter_config": params[5].obj,
                "status": "discovered", "permission_status": "unknown",
                "relationship_evidence": params[6].obj,
            }
            self.sources.append(source)
            return FakeResult(source)
        raise AssertionError(f"Unexpected SQL: {query}")
