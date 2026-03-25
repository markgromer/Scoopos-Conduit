"""
Conduit API - main FastAPI application entry point.
"""
import logging
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from backend.config import settings
from backend.database import engine, Base
from backend.api.auth import router as auth_router
from backend.api.agents import router as agents_router
from backend.api.dashboard import router as dashboard_router
from backend.api.webhooks import router as webhooks_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    async with engine.begin() as conn:
        # Import all models so they register with Base
        import backend.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")
    yield
    await engine.dispose()


app = FastAPI(
    title="Conduit",
    description="AI-powered multi-channel lead conversion platform for service businesses",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(dashboard_router)
app.include_router(webhooks_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "conduit"}


@app.get("/")
async def root():
    """Serve the SPA if present, otherwise confirm the backend is running."""
    index_html = STATIC_DIR / "index.html"
    if index_html.is_file():
        return FileResponse(index_html)
    return {"status": "ok", "service": "conduit", "message": "Backend is running (frontend not built)."}


@app.get("/data-deletion", response_class=HTMLResponse)
async def data_deletion():
    support_email = settings.support_email
    html = f"""<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Data Deletion Instructions</title>
        <style>
            body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height: 1.5; margin: 0; padding: 24px; color: #111; }}
            .wrap {{ max-width: 820px; margin: 0 auto; }}
            h1 {{ margin: 0 0 8px; font-size: 24px; }}
            p {{ margin: 12px 0; }}
            ol {{ margin: 12px 0 12px 20px; }}
            code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 6px; }}
            .muted {{ color: #444; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class=\"wrap\">
            <h1>Data Deletion Instructions</h1>
            <p class=\"muted\">Last updated: {datetime.utcnow().strftime('%Y-%m-%d')} (UTC)</p>

            <p>
                If you want us to delete your data from Conduit, email <a href=\"mailto:{support_email}\">{support_email}</a>.
            </p>

            <p>In your request, include:</p>
            <ol>
                <li>Your account email address.</li>
                <li>If applicable, the Facebook Page or Instagram account you connected.</li>
                <li>The subject line <code>Data Deletion Request</code>.</li>
            </ol>

            <p>
                We will verify the request and delete your account data and any connected integration data that we control.
                Some records may be retained if required for security, fraud prevention, or legal compliance.
            </p>

            <p class=\"muted\">
                If you used Facebook Login with Conduit, you can also remove the app from your Facebook settings.
            </p>
        </div>
    </body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    support_email = settings.support_email
    html = f"""<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Privacy Policy</title>
        <style>
            body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height: 1.5; margin: 0; padding: 24px; color: #111; }}
            .wrap {{ max-width: 820px; margin: 0 auto; }}
            h1 {{ margin: 0 0 8px; font-size: 24px; }}
            h2 {{ margin: 20px 0 8px; font-size: 18px; }}
            p {{ margin: 12px 0; }}
            ul {{ margin: 12px 0 12px 20px; }}
            code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 6px; }}
            .muted {{ color: #444; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class=\"wrap\">
            <h1>Privacy Policy</h1>
            <p class=\"muted\">Last updated: {datetime.utcnow().strftime('%Y-%m-%d')} (UTC)</p>

            <p>
                This policy explains how Conduit collects, uses, and shares information when you use the Conduit web app and related services.
            </p>

            <h2>Information we collect</h2>
            <ul>
                <li><strong>Account data</strong> such as your email and company name.</li>
                <li><strong>Lead and conversation data</strong> you process through connected channels (for example: message content, phone numbers, email addresses, names) as configured by you.</li>
                <li><strong>Integration data</strong> such as tokens/identifiers needed to connect to third-party services (for example Meta, Twilio, SendGrid, CRMs).</li>
                <li><strong>Usage and technical data</strong> such as logs and basic device/browser information.</li>
            </ul>

            <h2>How we use information</h2>
            <ul>
                <li>To provide and operate the service (including routing messages and generating AI-assisted responses).</li>
                <li>To secure the service, prevent abuse, and troubleshoot issues.</li>
                <li>To improve features and reliability.</li>
            </ul>

            <h2>Sharing</h2>
            <p>
                You may connect third-party services. When you do, Conduit may send and receive data with those services as required to provide the integration.
            </p>

            <h2>Retention</h2>
            <p>
                We retain data for as long as needed to provide the service and as required for security, legal, or compliance purposes.
            </p>

            <h2>Your choices</h2>
            <p>
                You can request deletion of your data by following the instructions at <a href=\"/data-deletion\">/data-deletion</a>.
            </p>

            <h2>Contact</h2>
            <p>
                Questions about this policy can be sent to <a href=\"mailto:{support_email}\">{support_email}</a>.
            </p>
        </div>
    </body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service():
    support_email = settings.support_email
    html = f"""<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Terms of Service</title>
        <style>
            body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height: 1.5; margin: 0; padding: 24px; color: #111; }}
            .wrap {{ max-width: 820px; margin: 0 auto; }}
            h1 {{ margin: 0 0 8px; font-size: 24px; }}
            h2 {{ margin: 20px 0 8px; font-size: 18px; }}
            p {{ margin: 12px 0; }}
            ul {{ margin: 12px 0 12px 20px; }}
            .muted {{ color: #444; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class=\"wrap\">
            <h1>Terms of Service</h1>
            <p class=\"muted\">Last updated: {datetime.utcnow().strftime('%Y-%m-%d')} (UTC)</p>

            <p>
                These terms govern your use of the Conduit web app and related services. By using the service, you agree to these terms.
            </p>

            <h2>Use of the service</h2>
            <ul>
                <li>You are responsible for activity under your account and for configuring integrations you connect.</li>
                <li>You agree not to misuse the service or attempt unauthorized access.</li>
            </ul>

            <h2>Third-party services</h2>
            <p>
                The service may integrate with third-party providers. Your use of those providers is governed by their terms.
            </p>

            <h2>Contact</h2>
            <p>
                Questions about these terms can be sent to <a href=\"mailto:{support_email}\">{support_email}</a>.
            </p>
        </div>
    </body>
</html>"""
    return HTMLResponse(content=html)


# ── Serve React frontend (production builds copied by render-build.sh) ──
if STATIC_DIR.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Catch-all: serve index.html for client-side routing."""
        # Don't intercept /api or backend-owned public endpoints.
        # Note: this function matches everything, so it must explicitly
        # allow server-rendered legal/compliance pages to work.
        normalized = full_path.rstrip("/")
        if (
            normalized.startswith("api/")
            or normalized in {"health", "openapi.json", "docs", "redoc"}
        ):
            return

        if normalized == "data-deletion":
            return await data_deletion()
        if normalized == "privacy-policy":
            return await privacy_policy()
        if normalized == "terms-of-service":
            return await terms_of_service()

        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
