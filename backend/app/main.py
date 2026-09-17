from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import aura, events, stocks, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PeerIPO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(events.router)
app.include_router(aura.router)
app.include_router(stocks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
