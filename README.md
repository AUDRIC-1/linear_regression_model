# Crop Yield Prediction

## Mission
Helping smallholder farmers plan fertilizer and irrigation decisions by predicting
crop yield (tons/hectare) from environmental and farming-practice data. Better yield
forecasts mean better-informed resource use before the growing season starts.

## Dataset
[Agriculture Crop Yield](https://www.kaggle.com/datasets/samuelotiattakorah/agriculture-crop-yield)
(Kaggle) — 1,000,000 rows covering region, soil type, crop, rainfall, temperature,
fertilizer/irrigation use, weather condition, and days to harvest.

## API
Public Swagger UI: https://linear-regression-model-g3rf.onrender.com/docs

Note: the free Render tier spins down after inactivity — the first request after
idle time can take up to ~50 seconds to respond.

## Video Demo
https://www.youtube.com/watch?v=mhV0xNxL_x4


## Running the Mobile App
1. Install Flutter (3.19+) and have a connected Android device or emulator.
2. From `summative/FlutterApp/`:
   ```bash
   flutter pub get
   flutter run
   ```
3. Fill in all 9 fields (Region, Soil Type, Crop, Weather Condition, Rainfall,
   Temperature, Fertilizer Used, Irrigation Used, Days to Harvest) and tap Predict.

## Project Structure
```
linear_regression_model/
├── summative/
│   ├── linear_regression/
│   │   └── multivariate.ipynb
│   ├── API/
│   │   ├── prediction.py
│   │   └── requirements.txt
│   └── FlutterApp/
├── pyproject.toml
```
