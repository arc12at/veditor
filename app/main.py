from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.queue import redis_conn
from app.routes import admin, auth, client, events, jobs, ops, reviews, studio, talks
from app.ui.templating import templates

app = FastAPI(title="VEditor API")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> Response:
    if "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            request, "404.html.jinja", {}, status_code=404
        )
    return JSONResponse(
        {"detail": getattr(exc, "detail", "Not Found")},
        status_code=404,
        headers=getattr(exc, "headers", None),
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
