import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from database import engine

app = FastAPI()


@app.on_event("startup")
def test_db_connection():
    try:
        with engine.connect() as conn:
            print("DB 연결 성공")
    except OperationalError as e:
        print("DB 연결 실패 (OperationalError):", e)
    except Exception as e:
        print("DB 연결 실패 (기타 오류):", e)


@app.get("/")
def root():
    return {"message": "Gravity backend running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
