import re
from collections.abc import Mapping
from typing import Any


def workday_cxs_base_url(config: Mapping[str, Any]) -> str:
    prefix, tenant, site = (
        config.get(key) for key in ("host_prefix", "tenant", "site")
    )
    if not all(isinstance(v, str) and v for v in (prefix, tenant, site)):
        raise ValueError("Workday config requires host_prefix, tenant and site.")
    if not re.fullmatch(r"[a-z0-9-]+\.wd[0-9]+", prefix):
        raise ValueError("Workday host_prefix is invalid.")
    if prefix.split(".")[0] != tenant or not re.fullmatch(r"[a-z0-9-]+", tenant):
        raise ValueError("Workday tenant does not match host_prefix.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", site):
        raise ValueError("Workday site identifier is invalid.")
    return f"https://{prefix}.myworkdayjobs.com/wday/cxs/{tenant}/{site}"
