from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.model import predict_churn
from app.schemas import CustomerFeatures

app = FastAPI(
    title="Customer Analytics & Churn Prediction Platform",
    version="1.2.0",
    description="Customer Analytics & Churn Prediction API",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

HTML_DASHBOARD = (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "customer_analytics_churn_api",
        "version": "1.2.0",
        "model_loaded": True
    }


@app.get("/api/metrics")
def get_metrics():
    return {
        "total_revenue_brl": 13591643.70,
        "total_orders": 99441,
        "total_customers": 96096,
        "average_order_value_brl": 137.75,
        "customers_in_training_data": 75387,
        "one_time_buyers_share": 0.970,
        "historical_churn_rate": 0.647,
        "model_accuracy": 0.998,
        "honest_test_roc_auc": 0.667,
        "data_source": {
            "company": "Olist",
            "website": "https://olist.com",
            "dataset": (
                "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
            ),
        },
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" not in accept and "application/json" in accept:
        return JSONResponse({"message": "Churn API is running"})
    return HTMLResponse(content=HTML_DASHBOARD)


@app.post("/predict")
def predict(customer: CustomerFeatures):
    features = [
        customer.frequency,
        customer.monetary,
        customer.recency,
        customer.avg_order_value,
    ]
    result = predict_churn(features)
    return result
