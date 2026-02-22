import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

class BaselineClassifier:
    def __init__(self):
        # We initialize a pipeline with TF-IDF and MultinomialNB
        self.pipeline = make_pipeline(
            TfidfVectorizer(stop_words='english'),
            MultinomialNB()
        )
        self._train_dummy_model()

    def _train_dummy_model(self):
        # Dummy training data to bootstrap the classifier
        # In a real scenario, this would be loaded from a dataset
        texts = [
            "I need help with my invoice and billing details.",
            "My credit card was charged twice.",
            "Can I change my payment method?",
            
            "The system keeps crashing when I login.",
            "I am getting a 500 internal server error.",
            "The API endpoint is returning timeout errors.",
            
            "I need a copy of the terms of service.",
            "We want to discuss the GDPR compliance and privacy policy.",
            "Our legal team wants to review the contract.",
        ]
        labels = [
            "Billing", "Billing", "Billing",
            "Technical", "Technical", "Technical",
            "Legal", "Legal", "Legal"
        ]
        self.pipeline.fit(texts, labels)

    def predict_category(self, text: str) -> str:
        """Predicts whether the text is Billing, Technical, or Legal."""
        prediction = self.pipeline.predict([text])
        return prediction[0]

def check_urgency(text: str) -> bool:
    """
    Regex-based heuristic for urgency.
    Flags keywords like 'broken', 'asap', 'urgent', 'down', 'critical'.
    """
    pattern = re.compile(r'\b(broken|asap|urgent|down|critical|emergency)\b', re.IGNORECASE)
    return bool(pattern.search(text))
