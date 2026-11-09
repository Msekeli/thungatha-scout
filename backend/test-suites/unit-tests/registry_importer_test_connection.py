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
            row = next(
                (item for item in self.employers if item["name"] == params[0]), None
            )
            return FakeResult(row)
        if "UPDATE employers SET website_url" in query:
            row = next(item for item in self.employers if item["id"] == params[1])
            row["website_url"] = params[0]
            return FakeResult(row)
        if "INSERT INTO employers" in query:
            row = {"id": uuid4(), "name": params[0], "website_url": params[1]}
            self.employers.append(row)
            return FakeResult(row)
        if "SELECT id, employer_id, adapter_key" in query:
            row = next(
                (item for item in self.sources if item["normalized_url"] == params[0]),
                None,
            )
            return FakeResult(row)
        if "SELECT id, normalized_url" in query:
            rows = [
                item
                for item in self.sources
                if item["employer_id"] == params[0] and item["adapter_key"] == params[1]
            ]
            return FakeResult(rows)
        if "UPDATE employer_sources" in query:
            row = next(item for item in self.sources if item["id"] == params[4])
            row.update(
                {
                    "source_url": params[0],
                    "employer_careers_url": params[1],
                    "normalized_url": params[2] or row["normalized_url"],
                    "adapter_config": params[3].obj,
                }
            )
            return FakeResult(row)
        if "INSERT INTO employer_sources" in query:
            row = {
                "id": uuid4(),
                "employer_id": params[0],
                "adapter_key": params[1],
                "source_url": params[2],
                "employer_careers_url": params[3],
                "normalized_url": params[4],
                "adapter_config": params[5].obj,
            }
            self.sources.append(row)
            return FakeResult(row)
        raise AssertionError(f"Unexpected SQL: {query}")
