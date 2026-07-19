# Mekhala AI Flood Assistant

Mekhala AI is an AI-assisted flood risk detection and response system developed for a university Artificial Intelligence project.

## Main Modules

1. Flood Risk Predictor
   - Predicts flood probability from environmental and infrastructure parameters.
   - Uses a trained scikit-learn regression model.

2. AI Flood Assistant
   - Provides flood-related guidance.
   - Supports multilingual flood-safety questions.
   - Uses disaster response intent classification, flood safety knowledge base, and guardrails.

3. Image Analysis
   - Classifies uploaded images into Flood, Non_Flood, or Unrelated.
   - Uses a ResNet18 image classifier.

## Tech Stack

- Python
- Streamlit
- scikit-learn
- PyTorch
- Pillow
- pandas
- NumPy
- deep-translator
- langdetect

## How to Run

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py