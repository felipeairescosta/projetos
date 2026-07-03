from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from .config import get_settings

_security = HTTPBearer(auto_error=False)


def get_supabase(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
) -> Client:
    """Cria um cliente Supabase autenticado com o JWT do usuário, para que
    as políticas de RLS sejam aplicadas de acordo com o usuário logado."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não informado.",
        )

    settings = get_settings()
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.postgrest.auth(credentials.credentials)
    return client


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    client: Client = Depends(get_supabase),
):
    try:
        user = client.auth.get_user(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada.",
        ) from exc

    if user is None or user.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada.",
        )
    return user.user
