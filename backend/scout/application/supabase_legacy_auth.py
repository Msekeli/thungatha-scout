import httpx
from jwt.exceptions import InvalidTokenError


class AuthenticationServiceUnavailable(RuntimeError):
    """Raised when Supabase cannot verify an access token."""


async def verify_legacy_access_token(
    token: str,
    supabase_url: str,
    publishable_key: str,
) -> dict[str, str | None]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "apikey": publishable_key,
                    "Authorization": f"Bearer {token}",
                },
            )
    except httpx.HTTPError as error:
        raise AuthenticationServiceUnavailable from error
    if response.status_code == 401:
        raise InvalidTokenError("Supabase rejected the access token.")
    if response.status_code != 200:
        raise AuthenticationServiceUnavailable(
            f"Supabase Auth returned HTTP {response.status_code}."
        )
    try:
        user = response.json()
    except ValueError as error:
        raise AuthenticationServiceUnavailable(
            "Supabase Auth returned an invalid response."
        ) from error
    if not isinstance(user, dict) or not user.get("id"):
        raise AuthenticationServiceUnavailable(
            "Supabase Auth returned an incomplete user response."
        )
    return {
        "sub": user["id"],
        "email": user.get("email"),
        "role": "authenticated",
    }
