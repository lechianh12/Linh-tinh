from fastapi import FastAPI
from api_router import router
from database import init_db
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],  # hoặc ["*"] để cho tất cả
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
async def connect():
    await init_db()

app.include_router(router, prefix='/api')
import uvicorn



if __name__ == "__main__":
    uvicorn.run(
        "main:app",   
        host="127.0.0.1",
        port=4000,
        reload=True
    )