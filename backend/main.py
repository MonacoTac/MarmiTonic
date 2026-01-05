from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import cocktails, ingredients, sparql

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cocktails.router, prefix="/cocktails", tags=["cocktails"])
app.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(sparql.router, prefix="/sparql", tags=["sparql"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}