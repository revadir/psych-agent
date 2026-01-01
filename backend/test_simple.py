from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/auth/login")
def login():
    return {"access_token": "test_token", "token_type": "bearer"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
