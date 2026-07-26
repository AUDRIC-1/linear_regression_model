#!/usr/bin/env python3
"""FastAPI service for crop yield prediction"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os

app = FastAPI(
    title="Crop Yield Prediction API",
    description="Predicts crop yield (tons/hectare) for smallholder farmers "
                "based on environmental and farming-practice data.",
    version="1.0.0"
)

# CORS: only allow the Flutter app's origin(s) and the methods/headers it
# actually needs, instead of a wildcard. Flutter web builds typically run
# on localhost during dev, and the deployed API only needs to accept
# POST (predict/retrain) and GET (docs) requests with JSON headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(os.path.dirname(__file__), "preprocessor.pkl")

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)


class CropInput(BaseModel):
    Region: str = Field(..., description="North, South, East, or West")
    Soil_Type: str = Field(..., description="Sandy, Clay, Loam, Silt, Peaty, or Chalky")
    Crop: str = Field(..., description="Crop type, e.g. Wheat, Rice, Maize")
    Weather_Condition: str = Field(..., description="Sunny, Rainy, or Cloudy")
    Rainfall_mm: float = Field(..., ge=0, le=3000, description="Rainfall in mm")
    Temperature_Celsius: float = Field(..., ge=-10, le=50, description="Avg temperature in Celsius")
    Fertilizer_Used: bool = Field(..., description="Whether fertilizer was applied")
    Irrigation_Used: bool = Field(..., description="Whether irrigation was used")
    Days_to_Harvest: int = Field(..., ge=1, le=365, description="Days to harvest")

    class Config:
        json_schema_extra = {
            "example": {
                "Region": "West",
                "Soil_Type": "Silt",
                "Crop": "Cotton",
                "Weather_Condition": "Sunny",
                "Rainfall_mm": 714.85,
                "Temperature_Celsius": 23.87,
                "Fertilizer_Used": False,
                "Irrigation_Used": False,
                "Days_to_Harvest": 120
            }
        }


class PredictionOutput(BaseModel):
    predicted_yield_tons_per_hectare: float


@app.get("/")
def root():
    return {"message": "Crop Yield Prediction API. Visit /docs for Swagger UI."}


@app.post("/predict", response_model=PredictionOutput)
def predict(data: CropInput):
    try:
        row = pd.DataFrame([{
            "Region": data.Region,
            "Soil_Type": data.Soil_Type,
            "Crop": data.Crop,
            "Weather_Condition": data.Weather_Condition,
            "Rainfall_mm": data.Rainfall_mm,
            "Temperature_Celsius": data.Temperature_Celsius,
            "Fertilizer_Used": int(data.Fertilizer_Used),
            "Irrigation_Used": int(data.Irrigation_Used),
            "Days_to_Harvest": data.Days_to_Harvest,
        }])
        processed = preprocessor.transform(row)
        prediction = model.predict(processed)[0]
        return PredictionOutput(predicted_yield_tons_per_hectare=float(prediction))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/retrain")
def retrain(file_path: str = "new_data.csv"):
    """Retrains the model using a new CSV of the same schema as the
    training data, if present, and overwrites the saved model."""
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=404,
            detail=f"{file_path} not found. Upload new data with this "
                   f"filename to the API folder to trigger retraining."
        )

    df = pd.read_csv(full_path)
    df["Fertilizer_Used"] = df["Fertilizer_Used"].astype(int)
    df["Irrigation_Used"] = df["Irrigation_Used"].astype(int)

    categorical_cols = ["Region", "Soil_Type", "Crop", "Weather_Condition"]
    numeric_cols = ["Rainfall_mm", "Temperature_Celsius", "Fertilizer_Used",
                     "Irrigation_Used", "Days_to_Harvest"]

    X = df[categorical_cols + numeric_cols]
    y = df["Yield_tons_per_hectare"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    global preprocessor, model
    X_train_proc = preprocessor.fit_transform(X_train)
    new_model = LinearRegression()
    new_model.fit(X_train_proc, y_train)

    joblib.dump(new_model, MODEL_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    model = new_model

    return {"message": "Model retrained and saved successfully."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
