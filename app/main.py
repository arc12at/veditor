from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.queue import redis_conn
from app.routes import admin, auth, client, events, jobs, ops, reviews, studio, talks
from app.ui.templating import templates

app = FastAPI(title="VEditor API")


def _prefers_html(accept: str | None) -> bool:
    if not accept:
        return False
    html_q = 0.0
    json_q = 0.0
    for item in accept.split(","):
        parts = [p.strip() for p in item.split(";")]
        if not parts or not parts[0]:
            continue
        mime = parts[0].lower()
        q = 1.0
        for param in parts[1:]:
            if param.lower().startswith("q="):
                try:
                    q = float(param[2:])
                except ValueError:
                    q = 0.0
                break
        if mime in ("text/html", "application/xhtml+xml"):
            html_q = max(html_q, q)
        elif mime == "application/json":
            json_q = max(json_q, q)
    return html_q > 0.0 and html_q >= json_q


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> Response:
    if _prefers_html(request.headers.get("accept")):
        response = templates.TemplateResponse(
            request, "404.html.jinja", {}, status_code=404
        )
        response.headers["Vary"] = "Accept"
        return response

    headers = dict(getattr(exc, "headers", None) or {})
    vary = headers.get("Vary")
    headers["Vary"] = (
        f"{vary}, Accept"
        if vary and "accept" not in vary.lower()
        else (vary or "Accept")
    )
    return JSONResponse(
        {"detail": getattr(exc, "detail", "Not Found")},
        status_code=404,
        headers=headers,
    )


_STATIC_DIR = Path(__file__).parent / "ui" / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(client.router)
app.include_router(events.router)
app.include_router(ops.router)
app.include_router(talks.router)
app.include_router(reviews.router)
app.include_router(jobs.router)
app.include_router(studio.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/studio")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/health")
def health_check():
    redis_conn.ping()
    return {"status": "ok"}
