import pandas as pd
import pickle
import torch
from transformers import RobertaTokenizerFast, RobertaForSequenceClassification
import numpy as np

# Configuration
DATA_PATH = "D:/food Scanning/data/datas.csv"
MODEL_PATH = "D:/food Scanning/finetuned_chemberta"
LABEL_ENCODER_PATH = "D:/food Scanning/label_encoder.pkl"

# Load LabelEncoder
try:
    with open(LABEL_ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"LabelEncoder not found at {LABEL_ENCODER_PATH}. Run finetune_chemberta.py first.")

# Load model and tokenizer
try:
    tokenizer = RobertaTokenizerFast.from_pretrained(MODEL_PATH)
    model = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()  # Set to evaluation mode
except Exception as e:
    raise Exception(f"Failed to load model/tokenizer from {MODEL_PATH}: {str(e)}")

# Load data
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
if not all(col in df.columns for col in ["E Number", "Ingredient", "Category", "Description"]):
    raise KeyError(f"Required columns ['E Number', 'Ingredient', 'Category', 'Description'] not found in {DATA_PATH}")

def predict_category(ingredient):
    """Predict category for an ingredient."""
    inputs = tokenizer(ingredient, padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1).numpy()[0]
        pred_idx = logits.argmax(-1).item()
        confidence = probs[pred_idx]
        pred_category = label_encoder.inverse_transform([pred_idx])[0]
    return pred_category, confidence

def show(e_number, ingredient=None):
    """
    Returns prediction results for a given E Number or ingredient.
    If E Number is not found, ingredient must be provided.
    Returns a dictionary with results.
    """
    try:
        match = df[df["E Number"].astype(str).str.strip().str.lower() == str(e_number).strip().lower()]
        if not match.empty:
            ingredient_val = match["Ingredient"].iloc[0]
            true_category = match["Category"].iloc[0]
            description = match["Description"].iloc[0]
            training_status = "Ingredient was used in model training."
        else:
            if not ingredient:
                return {
                    "error": f"E Number '{e_number}' not found and no ingredient provided."
                }
            ingredient_val = ingredient
            true_category = "Unknown"
            description = "Description not found in datas.csv."
            training_status = "Limited model training: Ingredient not in training data."
        # Predict category
        pred_category, confidence = predict_category(ingredient_val)
        return {
            "E Number": e_number,
            "Ingredient": ingredient_val,
            "True Category": true_category,
            "Predicted Category": pred_category,
            "Confidence": f"{confidence:.2%}",
            "Description": description,
            "Training Status": training_status
        }
    except Exception as e:
        return {"error": f"Error processing '{e_number}': {str(e)}"}