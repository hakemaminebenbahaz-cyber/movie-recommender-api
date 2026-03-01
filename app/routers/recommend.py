from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie as MovieModel
from app.schemas.movie import Movie, RecommendRequest, RecommendResponse
from app.services.recommender import recommender

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post("/", response_model=List[RecommendResponse])
def recommend_movies(request: RecommendRequest, db: Session = Depends(get_db)):
    """
    Return up to *n* movie recommendations based on a list of liked movie IDs.

    The model uses item-based collaborative filtering: movies that were
    consistently rated highly by the same users as your liked movies are
    surfaced first.
    """
    if not recommender.is_trained:
        raise HTTPException(
            status_code=503,
            detail="Recommender model is still training — please retry in a moment.",
        )

    results = recommender.recommend(request.liked_movie_ids, request.n)
    if not results:
        raise HTTPException(
            status_code=404,
            detail="None of the provided movie IDs are in the model index.",
        )

    recommendations: List[RecommendResponse] = []
    for movie_id, score in results:
        movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
        if movie:
            recommendations.append(
                RecommendResponse(movie=Movie.model_validate(movie), score=round(score, 4))
            )

    return recommendations
