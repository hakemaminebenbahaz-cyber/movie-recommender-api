import logging
import os

import pandas as pd
from sqlalchemy import text

from app.config import settings
from app.database import engine

logger = logging.getLogger(__name__)


def load_data() -> None:
    """Load MovieLens CSV data into PostgreSQL if the tables are empty."""
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM movies")).scalar()
        if count > 0:
            logger.info(f"Database already contains {count} movies — skipping CSV load.")
            return

    logger.info("Loading movies.csv …")
    movies_df = pd.read_csv(os.path.join(settings.DATA_DIR, "movies.csv"))
    movies_df = movies_df.rename(columns={"movieId": "id"})
    movies_df.to_sql("movies", engine, if_exists="append", index=False)
    logger.info(f"  → {len(movies_df)} movies inserted.")

    logger.info("Loading ratings.csv …")
    ratings_df = pd.read_csv(os.path.join(settings.DATA_DIR, "ratings.csv"))
    ratings_df = ratings_df.rename(
        columns={"userId": "user_id", "movieId": "movie_id"}
    )
    ratings_df.to_sql(
        "ratings", engine, if_exists="append", index=False,
        chunksize=10_000, method="multi",
    )
    logger.info(f"  → {len(ratings_df)} ratings inserted.")
