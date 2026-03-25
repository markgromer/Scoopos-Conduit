import uuid
from datetime import datetime, timedelta, timezone
import logging
import secrets
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, URLSafeSerializer
import httpx

from backend.config import settings
from backend.database import get_db
from backend.models.user import User
from backend.models.oauth_account import OAuthAccount
from backend.schemas.user import UserCreate, UserLogin, UserOut, Token

router = APIRouter(prefix="/api/auth", tags=["auth"])
# Use PBKDF2-SHA256 (pure Python) to avoid native build issues on deploy.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

logger = logging.getLogger(__name__)


def _state_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(settings.secret_key, salt="conduit-oauth-state")


def _make_state(provider: str) -> str:
    return _state_serializer().dumps({"p": provider, "ts": int(time.time())})


def _parse_state(provider: str, state: str) -> None:
    try:
        data = _state_serializer().loads(state)
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    if data.get("p") != provider:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    ts = int(data.get("ts") or 0)
    if ts <= 0 or (time.time() - ts) > 10 * 60:
        raise HTTPException(status_code=400, detail="OAuth state expired")


def _default_company_name(display_name: str | None, email: str | None) -> str:
    if display_name and display_name.strip():
        return display_name.strip()[:255]
    if email and "@" in email:
        return email.split("@", 1)[0][:255]
    return "New Account"


def _oauth_redirect_to_spa(token: str) -> RedirectResponse:
    # SPA route handled by the frontend router; backend will serve index.html.
    return RedirectResponse(url=f"/auth/callback?token={token}", status_code=302)


async def _get_or_create_user_for_oauth(
    *,
    db: AsyncSession,
    provider: str,
    provider_account_id: str,
    email: str | None,
    name: str | None,
) -> User:
    # 1) Existing OAuth link
    existing_oauth = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id,
        )
    )
    oauth_account = existing_oauth.scalar_one_or_none()
    if oauth_account:
        result = await db.execute(select(User).where(User.id == oauth_account.user_id))
        user = result.scalar_one()
        return user

    # 2) If email matches existing user, link to it
    user: User | None = None
    if email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    # 3) Otherwise create a new user
    if not user:
        random_password = secrets.token_urlsafe(48)
        user = User(
            email=email or f"{provider}-{provider_account_id}@oauth.local",
            hashed_password=_hash_password(random_password),
            company_name=_default_company_name(name, email),
        )
        db.add(user)
        await db.flush()

    # 4) Create OAuthAccount link
    db.add(
        OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_account_id=provider_account_id,
            email=email,
            name=name,
        )
    )
    return user


def _provider_config(provider: str):
    if provider == "google":
        if not settings.google_client_id or not settings.google_client_secret:
            raise HTTPException(status_code=503, detail="Google OAuth is not configured")
        return {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scopes": "openid email profile",
        }
    if provider == "facebook":
        if not settings.facebook_client_id or not settings.facebook_client_secret:
            raise HTTPException(status_code=503, detail="Facebook OAuth is not configured")
        return {
            "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "scopes": "email,public_profile",
        }
    raise HTTPException(status_code=404, detail="Unknown OAuth provider")


@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, request: Request, return_url: bool = False):
    cfg = _provider_config(provider)
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))
    state = _make_state(provider)

    if provider == "google":
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": cfg["scopes"],
            "state": state,
            "prompt": "select_account",
        }
        url = httpx.URL(cfg["auth_url"]).copy_merge_params(params)
        if return_url:
            return {"url": str(url)}
        return RedirectResponse(str(url), status_code=302)

    if provider == "facebook":
        params = {
            "client_id": settings.facebook_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": cfg["scopes"],
            "state": state,
        }
        url = httpx.URL(cfg["auth_url"]).copy_merge_params(params)
        if return_url:
            return {"url": str(url)}
        return RedirectResponse(str(url), status_code=302)

    raise HTTPException(status_code=404, detail="Unknown OAuth provider")


@router.get("/oauth/{provider}/callback", name="oauth_callback")
async def oauth_callback(provider: str, request: Request, code: str | None = None, state: str | None = None, db: AsyncSession = Depends(get_db)):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code/state")
    _parse_state(provider, state)
    cfg = _provider_config(provider)
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            if provider == "google":
                token_resp = await client.post(
                    cfg["token_url"],
                    data={
                        "code": code,
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                token_resp.raise_for_status()
                token = token_resp.json()
                access_token = token.get("access_token")
                if not access_token:
                    raise HTTPException(status_code=400, detail="OAuth token exchange failed")

                profile_resp = await client.get(
                    "https://openidconnect.googleapis.com/v1/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                profile_resp.raise_for_status()
                profile = profile_resp.json()

                provider_account_id = str(profile.get("sub") or "")
                email = profile.get("email")
                name = profile.get("name")
                if not provider_account_id:
                    raise HTTPException(status_code=400, detail="OAuth profile missing id")

            elif provider == "facebook":
                token_resp = await client.get(
                    cfg["token_url"],
                    params={
                        "client_id": settings.facebook_client_id,
                        "client_secret": settings.facebook_client_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                )
                token_resp.raise_for_status()
                token = token_resp.json()
                access_token = token.get("access_token")
                if not access_token:
                    raise HTTPException(status_code=400, detail="OAuth token exchange failed")

                profile_resp = await client.get(
                    "https://graph.facebook.com/me",
                    params={"fields": "id,name,email", "access_token": access_token},
                )
                profile_resp.raise_for_status()
                profile = profile_resp.json()

                provider_account_id = str(profile.get("id") or "")
                email = profile.get("email")
                name = profile.get("name")
                if not provider_account_id:
                    raise HTTPException(status_code=400, detail="OAuth profile missing id")
            else:
                raise HTTPException(status_code=404, detail="Unknown OAuth provider")

        user = await _get_or_create_user_for_oauth(
            db=db,
            provider=provider,
            provider_account_id=provider_account_id,
            email=email,
            name=name,
        )
        try:
            await db.commit()
        except IntegrityError:
            # Race condition creating the OAuthAccount link: rollback and re-fetch.
            await db.rollback()
            result = await db.execute(
                select(OAuthAccount).where(
                    OAuthAccount.provider == provider,
                    OAuthAccount.provider_account_id == provider_account_id,
                )
            )
            oauth_account = result.scalar_one_or_none()
            if not oauth_account:
                raise
            result = await db.execute(select(User).where(User.id == oauth_account.user_id))
            user = result.scalar_one()

        return _oauth_redirect_to_spa(_create_token(user.id))

    except httpx.HTTPError:
        await db.rollback()
        logger.exception("OAuth HTTP error")
        raise HTTPException(status_code=400, detail="OAuth request failed")
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        logger.exception("OAuth callback failed")
        raise HTTPException(status_code=500, detail="OAuth login failed")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


@router.post("/register", response_model=Token, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        hashed_password=_hash_password(body.password),
        company_name=body.company_name,
    )
    db.add(user)
    try:
        # Commit here so any DB errors surface predictably as an HTTP response
        # (instead of failing during dependency cleanup).
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    except Exception:
        await db.rollback()
        logger.exception("Register failed")
        raise HTTPException(status_code=500, detail="Registration failed")
    return Token(access_token=_create_token(user.id))


@router.post("/login", response_model=Token)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not _verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return Token(access_token=_create_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
