class FakeEmployerSourceUpdateService:
    def __init__(self) -> None:
        self.updated = None

    def update_configuration(self, employer_id, source_id, payload):
        self.updated = (employer_id, source_id, payload)
        return {
            "id": str(source_id),
            "employer_id": str(employer_id),
            "adapter_key": payload.adapter_key,
            "source_url": str(payload.source_url),
            "normalized_url": str(payload.normalized_url),
            "adapter_config": payload.adapter_config,
        }
