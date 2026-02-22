import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
from transformers import pipeline

class AdvancedClassifier:
    """
    Simulates loading a DistilBERT model for classification and urgency regression.
    Since we can't train a deep model during a short hackathon easily without data, 
    we use zero-shot classification for category, and sentiment analysis pipeline 
    as a proxy for the urgency score regression S in [0, 1].
    """
    def __init__(self):
        # We use a zero-shot classifier for routing our tickets (Billing, Technical, Legal)
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        # We use a sentiment analysis pipeline as a proxy for the urgency regression model.
        # "Negative" sentiment implies higher urgency in a support context usually.
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

        self.candidate_labels = ["Billing", "Technical", "Legal"]

    def analyze_ticket(self, text: str) -> dict:
        """
        Returns a dictionary with category and urgency score S in [0, 1].
        """
        # 1. Classification
        clf_result = self.classifier(text, self.candidate_labels)
        # The first label is the highest scoring one
        category = clf_result["labels"][0]
        
        # 2. Urgency Regression Score S in [0, 1]
        # DistilBERT Sentiment returns {"label": "NEGATIVE"/"POSITIVE", "score": 0.99...}
        # If NEGATIVE, we use the score as high urgency. If POSITIVE, we use 1 - score.
        sent_result = self.sentiment_analyzer(text)[0]
        
        if sent_result["label"] == "NEGATIVE":
            # high urgency
            urgency_score = sent_result["score"]
        else:
            # low urgency
            urgency_score = 1.0 - sent_result["score"]

        # To respect the hackathon constraint, let's bump the score artificially
        # if there are severe keywords, just in case the sentiment model is too polite.
        urgent_keywords = ["broken", "asap", "emergency", "critical", "down"]
        if any(keyword in text.lower() for keyword in urgent_keywords):
            urgency_score = max(urgency_score, 0.9)

        return {
            "category": category,
            "urgency_score": float(urgency_score) # Ensure it's a native float for JSON serialization
        }

# Instantiate a global instance to be loaded once in the worker
_classifier_instance = None

def get_classifier():
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = AdvancedClassifier()
    return _classifier_instance
