"""
Item-based collaborative filtering recommender.

Algorithm
---------
1. Build a user-item rating matrix from the MovieLens ratings CSV.
2. Compute pairwise cosine similarity between every pair of items (movies).
3. At query time, sum the similarity columns for each liked movie,
   zero-out already-liked movies, and return the top-N.
"""
import logging
import os

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings

logger = logging.getLogger(__name__)


class ItemBasedRecommender:
    def __init__(self) -> None:
        self._similarity_df: pd.DataFrame | None = None
        self.is_trained: bool = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train_from_csv(self, min_ratings: int = 5) -> None:
        """Train the model from ratings.csv.

        Parameters
        ----------
        min_ratings:
            Minimum number of ratings a movie must have to be included.
            Movies with fewer ratings are excluded to reduce noise.
        """
        path = os.path.join(settings.DATA_DIR, "ratings.csv")
        logger.info("Loading ratings.csv for training …")
        df = pd.read_csv(path)

        # Drop movies with too few ratings (cold-item filter)
        counts = df.groupby("movieId")["rating"].count()
        valid_movies = counts[counts >= min_ratings].index
        df = df[df["movieId"].isin(valid_movies)]

        n_users = df["userId"].nunique()
        n_movies = df["movieId"].nunique()
        logger.info(f"Building user-item matrix: {n_users} users × {n_movies} movies")

        user_item = df.pivot_table(
            index="userId",
            columns="movieId",
            values="rating",
            fill_value=0,
        )

        logger.info("Computing item-item cosine similarity …")
        # Transpose → items × users, then compute similarity between rows (items)
        sparse = csr_matrix(user_item.values.T, dtype=np.float32)
        sim = cosine_similarity(sparse)

        self._similarity_df = pd.DataFrame(
            sim.astype(np.float32),
            index=user_item.columns,
            columns=user_item.columns,
        )
        self.is_trained = True
        logger.info(f"Recommender ready — {len(self._similarity_df)} items indexed.")

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def recommend(
        self, liked_ids: list[int], n: int = 10
    ) -> list[tuple[int, float]]:
        """Return the top-N recommended (movie_id, score) pairs.

        Parameters
        ----------
        liked_ids:
            List of movie IDs the user already likes.
        n:
            Number of recommendations to return.
        """
        if not self.is_trained or self._similarity_df is None:
            raise ValueError("Model is not trained yet.")

        # Keep only IDs that exist in the similarity index
        valid = [i for i in liked_ids if i in self._similarity_df.index]
        if not valid:
            return []

        # Aggregate similarity scores across all liked movies
        scores: pd.Series = self._similarity_df[valid].sum(axis=1)

        # Exclude the input movies from results
        scores[valid] = 0

        top = scores.nlargest(n)
        return [(int(mid), float(score)) for mid, score in top.items()]


# Module-level singleton — shared across requests
recommender = ItemBasedRecommender()
