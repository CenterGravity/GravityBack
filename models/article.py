# app/models/article.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Article(Base):
    __tablename__ = "articles"

    # DTO: Articleresponse.articleId
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # DTO: ArticleBase.title
    title = Column(String(255), nullable=False)

    # DTO: ArticleBase.content
    content = Column(Text, nullable=False)

    # DTO: ArticleCreate.is_public
    is_public = Column(Boolean, nullable=False, default=True)

    # 글 작성/수정 시간 (추가 필드)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # 누가 쓴 글인지 (옵션 – 필요 없으면 제거)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    author = relationship("User", back_populates="articles")
