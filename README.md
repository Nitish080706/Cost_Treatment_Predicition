# Cost Prediction Treatment System

## Quick Fix for GitHub Push Error

The model files are too large for GitHub. Run these commands:

```bash
# Go to project root
cd N:\Projects\Costtreatment

# Remove the large files from git (files stay on disk)
git rm -r --cached backend/models/
git rm -r --cached models/
git rm -r --cached __pycache__/

# Stage all changes (includes updated .gitignore)
git add .

# Create new commit without large files
git commit -m "Remove large ML model files - train locally with train_ensemble.py"

# Force push to overwrite previous commit
git push -f origin main
```

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
