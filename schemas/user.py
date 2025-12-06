from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class userCreate(BaseModel):
    #회원 가입 로직 >:)
    username: str
    email: EmailStr
    created_at: datetime
