from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.article import Article
from models.user import User
from schemas.article import ArticleCreate, ArticleUpdate, Articleresponse
from utils.dependencies import get_db
from utils.security import ALGORITHM, SECRET_KEY, get_current_user

router = APIRouter()

optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _serialize_article(article: Article) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "is_public": article.is_public,
        "author_id": article.author_id,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
    }


def get_optional_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(optional_oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()


@router.post("/", response_model=Articleresponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = Article(
        title=article_in.title,
        content=article_in.content,
        is_public=article_in.is_public,
        author_id=current_user.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return {"articleId": article.id}


@router.get("/")
def list_articles(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="검색어"),
) -> List[dict]:
    query = db.query(Article).filter(Article.is_public.is_(True))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Article.title.ilike(like), Article.content.ilike(like)))

    articles = (
        query.order_by(Article.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return [_serialize_article(article) for article in articles]


@router.get("/{article_id}")
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    if not article.is_public and (not current_user or current_user.id != article.author_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비공개 게시글입니다.")

    return _serialize_article(article)


@router.patch("/{article_id}")
def update_article(
    article_id: int,
    article_in: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    article.title = article_in.title
    article.content = article_in.content
    db.add(article)
    db.commit()
    db.refresh(article)
    return _serialize_article(article)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다.")

    db.delete(article)
    db.commit()
    return None
