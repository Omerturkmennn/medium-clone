from pydantic import BaseModel
from typing import List
from app.schemas.post import PostResponse

class UserStatsResponse(BaseModel):
    total_articles: int
    total_views: int
    total_likes: int
    trending_posts: List[PostResponse]  #En çok okunan top 3 makale