from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie as MovieModel
from app.schemas.movie import Movie

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=List[Movie])
def list_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by title (case-insensitive)"),
    genre: Optional[str] = Query(None, description="Filter by genre (e.g. Action)"),
    db: Session = Depends(get_db),
):
    """List movies with optional title search and genre filter."""
    query = db.query(MovieModel)
    if search:
        query = query.filter(MovieModel.title.ilike(f"%{search}%"))
    if genre:
        query = query.filter(MovieModel.genres.ilike(f"%{genre}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get a single movie by its ID."""
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
