import logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from expense.api import router as expense_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Expense Tracker API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Include expense router
app.include_router(expense_router, prefix="/v1", tags=["Expense"])


# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI + uv!"}


@app.get("/health")
def health_check():
    return {"status": "Healthy"}


# Cache OpenAPI schema generation to avoid recomputation
@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
