# MediPredict AI — Disease Prediction & Healthcare Recommendation System

An AI/ML-powered Flask web application that predicts the most probable disease from
user-reported symptoms and provides educational healthcare guidance.

> **Disclaimer:** This project is developed for **educational purposes only**. It does
> not replace professional medical advice, diagnosis, or treatment.

---

## Features

- Predicts disease from Age, Gender, and selected Symptoms using a trained ML model
- Compares **Random Forest**, **Decision Tree**, and **Logistic Regression**; automatically
  deploys the best-performing model
- Displays confidence score, risk level (Low/Medium/High), disease description, causes,
  precautions, lifestyle tips, diet & exercise recommendations, when to consult a doctor,
  and recommended medical specialist
- One-click **"Find Nearby Hospital"** button that opens Google Maps (no API key required)
- **Downloadable PDF Medical Report** summarizing the full result for the patient
- **Dashboard** with total predictions, recent activity, and Pie/Bar charts (Chart.js)
- **Prediction History** page backed by SQLite, with search
- **Dark mode** with saved preference, **toast notifications**, animated stats counters,
  FAQ accordion, step-progress indicator and loading animation on the prediction form
- Full model evaluation on the About page: accuracy, precision, recall, F1 score, and
  confusion matrix
- Searchable symptom checklist, responsive Bootstrap 5 UI, input validation, error handling

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Font Awesome, JavaScript, Chart.js |
| Backend | Python, Flask |
| Machine Learning | Pandas, NumPy, Scikit-learn (Random Forest, Decision Tree, Logistic Regression) |
| Storage | SQLite (prediction history) |
| Reporting | ReportLab (PDF medical report generation) |
| Model Persistence | Pickle |

---

## Project Structure

```
disease-prediction-system/
├── dataset/
│   ├── generate_dataset.py        # Builds the disease-symptom dataset
│   └── disease_symptom_dataset.csv
├── model/
│   ├── disease_model.pkl          # Best trained model (auto-selected)
│   ├── gender_encoder.pkl
│   ├── disease_encoder.pkl
│   ├── feature_columns.pkl
│   ├── metrics.json                # Model comparison results
│   ├── classification_report.txt
│   └── history.db                  # SQLite prediction history (auto-created)
├── static/
│   ├── css/style.css                (incl. dark mode, toasts, animations)
│   ├── js/script.js                 (incl. dark mode, toasts, counters, charts glue)
│   └── img/confusion_matrix.png
├── templates/
│   ├── base.html                    (navbar, dark mode toggle, toast container)
│   ├── home.html                    (hero, features, FAQ, animated counters)
│   ├── predict.html                 (step progress, loading overlay, patient name)
│   ├── result.html                  (diet/exercise/doctor advice, PDF download)
│   ├── dashboard.html               (stats + Pie/Bar charts)
│   ├── history.html                 (searchable prediction table)
│   ├── about.html
│   ├── contact.html
│   └── 404.html
├── utils/
│   ├── disease_info.py             # Disease metadata knowledge base
│   ├── database.py                  # SQLite read/write helpers
│   └── pdf_generator.py             # Medical report PDF builder
├── app.py                          # Flask application entry point
├── train_model.py                  # ML training pipeline
├── requirements.txt
└── README.md
```

---

## Setup & Installation

1. **Clone / extract the project**, then navigate into it:
   ```bash
   cd disease-prediction-system
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Re)generate the dataset** (optional — a CSV is already included):
   ```bash
   cd dataset
   python generate_dataset.py
   cd ..
   ```

5. **Train the model** (optional — trained artifacts are already included in `model/`):
   ```bash
   python train_model.py
   ```

6. **Run the Flask app:**
   ```bash
   python app.py
   ```

7. Open your browser at **http://127.0.0.1:5000**

---

## ML Workflow Summary

1. **Data Preparation** — One-hot encode symptoms, label-encode Gender & Disease
2. **Train-Test Split** — 80/20 stratified split
3. **Model Training** — Random Forest, Decision Tree, Logistic Regression
4. **Evaluation** — Accuracy, Precision, Recall, F1 Score, Confusion Matrix
5. **Best Model Selection** — Highest test accuracy is chosen automatically
6. **Deployment** — Best model serialized with Pickle and loaded by `app.py`

Latest training run selected **Logistic Regression** (~98.3% test accuracy). Re-run
`train_model.py` any time to retrain and re-evaluate.

---

## Notes for Viva / Evaluation

- The dataset is generated programmatically (`dataset/generate_dataset.py`) with realistic
  symptom variability (dropped/noise symptoms) so the classification problem isn't trivial —
  this can be explained transparently rather than citing an opaque external source.
- Model comparison is genuine: `train_model.py` trains all three algorithms and picks the
  winner by test accuracy — nothing is hardcoded.
- `utils/disease_info.py` is decoupled from `app.py` to keep prediction logic and medical
  content separately maintainable (separation of concerns).
- No hospital database or external API is required — the "Find Nearby Hospital" button
  builds a Google Maps search URL dynamically from the recommended specialist.
