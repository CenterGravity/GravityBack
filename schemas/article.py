from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ArticleBase(BaseModel):
    #그냥 단순히 구조만 정해두는거
    title: str
    content: str

class ArticleCreate(ArticleBase):
    #create할때 어떤거 받아올건지
    is_public: bool
    pass

class ArticleUpdate(ArticleBase):
    pass

class Articleresponse(BaseModel):
    articleId: int