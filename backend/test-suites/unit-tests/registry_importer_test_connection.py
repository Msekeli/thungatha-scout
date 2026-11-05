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
            row = next((e for e in self.employers if e["name"] == params[0]), None)
            return FakeResult(row)
        if "INSERT INTO employers" in query:
            row = {
                "id": uuid4(), "name": params[0], "website_url": params[1],
                "location_evidence": params[3].obj,
            }
            self.employers.append(row)
            return FakeResult(row)
        if "SELECT id, employer_id, adapter_key" in query:
            row = next((s for s in self.sources if s["normalized_url"] == params[0]), None)
            return FakeResult(row)
        if "SELECT id, normalized_url" in query:
            rows = [
                s for s in self.sources
                if s["employer_id"] == params[0] and s["adapter_key"] == params[1]
            ]
            return FakeResult(rows)
        if "UPDATE employer_sources" in query:
            source_id = params[3] if len(params) == 4 else params[2]
            row = next(s for s in self.sources if s["id"] == source_id)
            row["source_url"] = params[0]
            if len(params) == 4:
                row["normalized_url"] = params[1]
                row["adapter_config"] = params[2].obj
            else:
                row["adapter_config"] = params[1].obj
            return FakeResult(row)
        if "INSERT INTO employer_sources" in query:
            row = {
                "id": uuid4(), "employer_id": params[0], "adapter_key": params[1],
                "source_url": params[2], "normalized_url": params[4],
                "adapter_config": params[5].obj, "status": "discovered",
                "permission_status": "unknown",
                "relationship_evidence": params[6].obj,
            }
            self.sources.append(row)
            return FakeResult(row)
        raise AssertionError(f"Unexpected SQL: {query}")
