from pathlib import Path
import joblib

API_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = API_DIR.parent

# Docker mounts ./ml at /app/ml. Vercel deploys api/ on its own,
# so it uses the bundled copy.
MODEL_CANDIDATES = [
    Path("/app/ml/models/churn_model.pkl"),
    BASE_DIR / "ml" / "models" / "churn_model.pkl",
    API_DIR / "models" / "churn_model.pkl",
]
MODEL_PATH = next(
    (p for p in MODEL_CANDIDATES if p.exists()),
    MODEL_CANDIDATES[-1],
)

model = None


def get_model():

    global model

    if model is None:
        model = joblib.load(MODEL_PATH)

    return model


def predict_churn(features):

    model = get_model()

    prediction = int(model.predict([features])[0])
    result = {
        "prediction": prediction,
        "churn_prediction": prediction,
    }
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba([features])[0]
        result["probability"] = round(float(probs[1]), 4)

    return result
