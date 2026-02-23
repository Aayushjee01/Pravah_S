# 🏠 NaviPrice — Navi Mumbai House Price Predictor

**AI-Powered Real Estate Valuation Platform for Navi Mumbai**

An end-to-end machine learning system that predicts residential property prices across 9+ localities in Navi Mumbai, India. Features a **FastAPI backend** with a trained Gradient Boosting model and a **Next.js frontend** with a premium dark-mode glassmorphism UI.

![NaviPrice](https://img.shields.io/badge/ML-Gradient_Boosting-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 🤖 Machine Learning
- **Gradient Boosting Regressor** trained on 2,200+ cleaned real estate transactions
- **R² = 0.849** on holdout test set
- Comprehensive data preprocessing pipeline handling messy real-world data
- Confidence score estimation using staged boosting predictions
- Feature importance analysis (Area drives 93.5% of predictions)

### 🚀 Backend (FastAPI)
- RESTful API with OpenAPI/Swagger documentation
- Pydantic request/response schemas with validation
- Health check, prediction, locations, and model-info endpoints
- Structured logging, CORS, and error handling
- Deployment-ready for **Render**

### 💎 Frontend (Next.js)
- Modern dark-mode UI with glassmorphism design
- Responsive layout (desktop, tablet, mobile)
- Real-time prediction results with confidence intervals
- Feature importance visualization bars
- Location market context cards
- Deployment-ready for **Vercel**

---

## 📁 Project Structure

```
Pravah_S/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py             # API endpoints
│   │   ├── core/
│   │   │   ├── config.py             # Settings & env vars
│   │   │   └── logging.py            # Structured logging
│   │   ├── ml/
│   │   │   ├── preprocessing.py      # Data cleaning pipeline
│   │   │   ├── predictor.py          # Inference engine
│   │   │   └── train.py              # Model training script
│   │   ├── schemas/
│   │   │   └── prediction.py         # Pydantic models
│   │   └── main.py                   # FastAPI app factory
│   ├── data/                         # Raw CSV dataset
│   ├── models/                       # Trained model artifacts
│   ├── tests/                        # Pytest test suite
│   ├── requirements.txt
│   ├── Procfile                      # Render deployment
│   ├── render.yaml                   # Render config
│   └── .env.example
│
├── frontend/                         # Next.js Frontend
│   ├── app/
│   │   ├── globals.css               # Design system
│   │   ├── layout.js                 # Root layout + SEO
│   │   ├── page.js                   # Main application
│   │   └── page.module.css           # Page styles
│   ├── .env.local                    # Local API URL
│   ├── .env.example                  # Vercel env template
│   └── package.json
│
├── navi_mumbai_real_estate_uncleaned_2500.csv
├── model.pkl.json                    # Duxport model config
└── README.md
```

---

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Train the ML model (first time only)
python -m app.ml.train

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at `http://localhost:3000`

### 3. Run Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

---

## 🔌 API Endpoints

| Method | Endpoint             | Description                          |
|--------|---------------------|--------------------------------------|
| GET    | `/`                  | Root — API info                      |
| GET    | `/api/v1/health`     | Health check + model status          |
| POST   | `/api/v1/predict`    | Generate price prediction            |
| GET    | `/api/v1/locations`  | List all locations with stats        |
| GET    | `/api/v1/model-info` | Model metadata and metrics           |

### Example Prediction Request

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Kharghar",
    "area_sqft": 1000,
    "bhk": 2,
    "bathrooms": 2,
    "floor": 10,
    "total_floors": 20,
    "age_of_property": 5,
    "parking": true,
    "lift": true
  }'
```

### Example Response

```json
{
  "predicted_price": 15299000,
  "price_range": {
    "low": 14075000,
    "high": 16523000
  },
  "price_per_sqft": 15299,
  "confidence_score": 0.91,
  "location_context": {
    "name": "Kharghar",
    "avg_price": 15700000,
    "median_price": 13700000,
    "avg_price_per_sqft": 14579,
    "data_points": 383
  },
  "feature_importance": {
    "area_sqft": 0.9353,
    "age_of_property": 0.0144,
    "total_floors": 0.0141,
    "bhk": 0.0137,
    "floor": 0.0121,
    "location": 0.0051,
    "bathrooms": 0.003,
    "lift": 0.0013,
    "parking": 0.0011
  }
}
```

---

## 🚀 Deployment

### Backend → Render

1. Push the `backend/` directory to a Git repository
2. Create a new **Web Service** on [Render](https://render.com)
3. Set the root directory to `backend`
4. Set build command: `pip install -r requirements.txt && python -m app.ml.train`
5. Set start command: `gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
6. Add environment variables:
   ```
   APP_ENV=production
   APP_DEBUG=false
   MODEL_PATH=models/house_price_model.joblib
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   LOG_LEVEL=WARNING
   ```

### Frontend → Vercel

1. Push the `frontend/` directory to a Git repository
2. Import the project on [Vercel](https://vercel.com)
3. Set the root directory to `frontend`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
5. Deploy — Vercel auto-detects Next.js

---

## 📊 Model Performance

| Metric     | Train  | Test   |
|-----------|--------|--------|
| R² Score  | 0.9175 | 0.849  |
| RMSE      | ₹24.0L | ₹33.4L |
| MAE       | ₹18.7L | ₹25.9L |
| MAPE      | 14.5%  | 19.3%  |

### Covered Locations
Airoli, Belapur, CBD Belapur, Ghansoli, Kharghar, Nerul, Panvel, Ulwe, Vashi

### Feature Importance
| Feature          | Importance |
|-----------------|------------|
| Carpet Area      | 93.5%      |
| Age of Property  | 1.4%       |
| Total Floors     | 1.4%       |
| BHK              | 1.4%       |
| Floor            | 1.2%       |
| Location         | 0.5%       |
| Bathrooms        | 0.3%       |
| Lift             | 0.1%       |
| Parking          | 0.1%       |

---

## 🧪 Testing

The project includes 40 tests covering:
- **API endpoint tests**: Health check, prediction (valid/invalid inputs), locations, model info
- **Preprocessing tests**: Location normalization, price cleaning, BHK parsing, floor handling, yes/no conversion

```bash
cd backend && source .venv/bin/activate
python -m pytest tests/ -v
# ======================== 40 passed in 0.92s =========================
```

---

## ⚙️ Tech Stack

| Component    | Technology                      |
|-------------|---------------------------------|
| ML Model    | scikit-learn (GradientBoostingRegressor) |
| Backend     | FastAPI + Uvicorn + Gunicorn    |
| Frontend    | Next.js 16 (App Router)        |
| Styling     | Vanilla CSS (Glassmorphism)     |
| Validation  | Pydantic v2                     |
| Testing     | Pytest                          |
| Deployment  | Render (API) + Vercel (Web)     |

---

## 📝 License

This project is part of Pravah. For educational and demonstration purposes.

---

*Built with ❤️ for Navi Mumbai homebuyers, sellers, and investors.*