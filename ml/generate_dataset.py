import pandas as pd
import random
from .clean import clean_text

# Keywords and scores
urgency_keywords = {"emergency":10, "urgent":10, "critical":9, "asap":8, "soon":4}
equipment_keywords = {"server":10, "network":10, "router":9, "database":9, "printer":5, "laptop":6}
impact_keywords = {"entire company":10, "all users":10, "everyone":10, "department":8, "my":2, "i":1}

priority_labels = ["Low", "Medium", "High", "Critical"]

# Simple templates (can expand)
templates = [
    "Server down urgently! All users cannot access database",
    "Printer not working, urgent reports needed",
    "My laptop is slow, can you check?",
    "Network router failed, entire company has no internet"
]

def calculate_score(text):
    text = text.lower()
    urgency = max([urgency_keywords[k] for k in urgency_keywords if k in text]+[0])
    equipment = max([equipment_keywords[k] for k in equipment_keywords if k in text]+[3])
    impact = max([impact_keywords[k] for k in impact_keywords if k in text]+[2])
    score = (urgency*0.4)+(equipment*0.35)+(impact*0.25)
    return score

def assign_label(score):
    if score >= 8: return "Critical"
    if score >= 6: return "High"
    if score >= 4: return "Medium"
    return "Low"

def generate_dataset(num_samples=500):
    data = []
    for i in range(num_samples):
        text = random.choice(templates)
        cleaned = clean_text(text)
        score = calculate_score(cleaned)
        label = assign_label(score)
        data.append({"complaint_text": text, "cleaned_text": cleaned, "priority": label})
    df = pd.DataFrame(data)
    df.to_csv("ml/dataset.csv", index=False)
    print("Dataset generated: ml/dataset.csv")

if __name__ == "__main__":
    generate_dataset()
