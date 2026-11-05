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
        if "INSERT INTO employers" in query:
            employer = {
                "id": uuid4(),
                "name": params[0],
                "website_url": params[1],
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
                row
                for row in self.sources
                if row["employer_id"] == params[0] and row["adapter_key"] == params[1]
            ]
            return FakeResult(matches)
        if "UPDATE employer_sources" in query:
            source_id = params[3] if len(params) == 4 else params[2]
            source = next(row for row in self.sources if row["id"] == source_id)
            source["source_url"] = params[0]
            if len(params) == 4:
                source["normalized_url"] = params[1]
                source["adapter_config"] = params[2].obj
            else:
                source["adapter_config"] = params[1].obj
            return FakeResult(source)
        if "INSERT INTO employer_sources" in query:
            source = {
                "id": uuid4(),
                "employer_id": params[0],
                "adapter_key": params[1],
                "source_url": params[2],
                "normalized_url": params[4],
                "adapter_config": params[5].obj,
                "status": "discovered",
                "permission_status": "unknown",
                "relationship_evidence": params[6].obj,
            }
            self.sources.append(source)
            return FakeResult(source)
        raise AssertionError(f"Unexpected SQL: {query}")
