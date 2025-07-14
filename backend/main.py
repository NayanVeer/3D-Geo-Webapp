from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="3D Geo WebApp Backend")

# Allow cross-origin requests from frontend (important for JS maps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production: replace * with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend running 🚀"}

@app.get("/api/hello")
async def hello():
    return {"result": "Hello from FastAPI!"}
