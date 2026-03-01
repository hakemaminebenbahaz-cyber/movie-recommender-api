from typing import List

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Movie(BaseModel):
    id: int
    title: str
    genres: str

    @computed_field
    @property
    def genres_list(self) -> List[str]:
        if self.genres == "(no genres listed)":
            return []
        return self.genres.split("|")

    model_config = ConfigDict(from_attributes=True)


class RecommendRequest(BaseModel):
    liked_movie_ids: List[int]
    n: int = Field(default=10, ge=1, le=50)


class RecommendResponse(BaseModel):
    movie: Movie
    score: float
