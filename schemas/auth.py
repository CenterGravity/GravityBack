from pydantic import BaseModel, EmailStr

class userLogin(BaseModel):
    #로그인
    email: EmailStr
    password: str

class Token(BaseModel):
    # 로그인 성공 시 응답(토큰용)
    access_token: str
    token_type: str = "bearer"