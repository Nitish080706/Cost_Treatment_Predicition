# Cost Prediction Treatment System


## Regenerate Models After Clone

When someone clones this repo, they need to:
```bash
cd backend
python train_ensemble.py
```

This will recreate all the `.pkl` model files locally.

---

## Project Overview
Medical cost prediction system with ML ensemble models, user authentication, and interactive visualizations.

## Tech Stack
- **Backend**: Python, Flask, MongoDB
- **ML**: Scikit-learn, XGBoost (5-model ensemble)
- **Frontend**: HTML/CSS/JavaScript, Three.js, Chart.js
- **Auth**: JWT, bcrypt

## Setup & Run
See [how_to_run.md](how_to_run.md) for detailed instructions.
