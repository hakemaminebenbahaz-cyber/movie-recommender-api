import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import movies, recommend
from app.services.loader import load_data
from app.services.recommender import recommender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create DB tables (idempotent)
    Base.metadata.create_all(bind=engine)

    # 2. Seed the database from CSV if needed
    load_data()

    # 3. Train the recommendation model in a background thread so the
    #    server stays responsive while the matrix is being built.
    thread = threading.Thread(target=recommender.train_from_csv, daemon=True)
    thread.start()

    yield  # server is running


app = FastAPI(
    title="Movie Recommender API",
    description=(
        "Item-based collaborative filtering built on MovieLens data.\n\n"
        "**Workflow**\n"
        "1. Search `/movies?search=inception` to find movie IDs.\n"
        "2. POST those IDs to `/recommend/` to get personalised suggestions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(movies.router)
app.include_router(recommend.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse("static/index.html")


@app.get("/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "model_trained": recommender.is_trained,
    }
