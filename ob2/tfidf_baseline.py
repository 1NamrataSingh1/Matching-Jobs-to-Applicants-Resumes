"""
TF-IDF + Logistic Regression baseline for job matching.
"""
import json
import os
import sys
import pickle
import numpy as np

# ======================================================================
# AUTO-DETECT ob2/ DIRECTORY
# ======================================================================
def _go_to_ob2():
    if os.path.exists('cv_analyzer.py'):
        return
    if os.path.isdir('ob2') and os.path.exists(os.path.join('ob2', 'cv_analyzer.py')):
        os.chdir('ob2')
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(script_dir, 'cv_analyzer.py')):
        os.chdir(script_dir)
        return

_go_to_ob2()
# ======================================================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from skills_query import QueryMysql


class TFIDFMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        # NOTE: multi_class was removed in sklearn 1.7+
        # multinomial is now the default behavior
        self.classifier = LogisticRegression(
            max_iter=1000,
            solver='lbfgs',
            class_weight='balanced'
        )
        self.label_encoder = LabelEncoder()
        self.q = QueryMysql()
        self.is_trained = False

    def train(self, resumes, job_codes):
        """Train on resume text -> job code pairs."""
        print(f"Training TF-IDF on {len(resumes)} examples...")

        valid = [(r, c) for r, c in zip(resumes, job_codes) if r and r.strip() and c and c.strip()]
        if not valid:
            raise ValueError("No valid training data!")
        resumes, job_codes = zip(*valid)

        from collections import Counter
        counts = Counter(job_codes)
        print(f"  {len(counts)} classes, {min(counts.values())}-{max(counts.values())} examples/class")

        X = self.vectorizer.fit_transform(resumes)
        y = self.label_encoder.fit_transform(job_codes)
        self.classifier.fit(X, y)
        self.is_trained = True
        print(f"  ✓ Trained: {X.shape[1]} features, {len(counts)} classes")

    def predict(self, resume, top_k=5):
        if not self.is_trained:
            raise ValueError("Model not trained!")
        if not resume or not resume.strip():
            return [(0, 0, 1, '', 'Unknown')] * top_k

        X = self.vectorizer.transform([resume])
        probs = self.classifier.predict_proba(X)[0]
        top_idx = np.argsort(probs)[-top_k:][::-1]
        top_codes = self.label_encoder.inverse_transform(top_idx)
        top_probs = probs[top_idx]

        results = []
        for code, prob in zip(top_codes, top_probs):
            try:
                info = self.q.get_job(code)
                title = info[0][1] if info else "Unknown"
            except Exception:
                title = "Unknown"
            results.append((float(prob), float(prob), 1.0, code, title))
        return results

    def save(self, path='tfidf_model.pkl'):
        with open(path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'label_encoder': self.label_encoder
            }, f)
        print(f"✓ Saved to {path}")

    def load(self, path='tfidf_model.pkl'):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Not found: {path}")
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.classifier = data['classifier']
            self.label_encoder = data['label_encoder']
            self.is_trained = True
        print(f"✓ Loaded from {path}")


def find_train_data():
    """Search multiple locations for training data."""
    for path in ['train_data.json', '../train_data.json']:
        if os.path.exists(path):
            print(f"Found: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

    # Try creating from prepare_test_data
    print("train_data.json not found, trying to create it...")
    try:
        from prepare_test_data import create_train_data
        return create_train_data()
    except Exception as e:
        print(f"  Failed: {e}")
    return None


def train_tfidf_baseline():
    data = find_train_data()
    if not data:
        print("ERROR: No training data!")
        sys.exit(1)

    resumes = [d.get('resume', d.get('text', '')) for d in data]
    codes = [d.get('job_code', d.get('onetsoc_code', '')) for d in data]

    model = TFIDFMatcher()
    model.train(resumes, codes)
    model.save('tfidf_model.pkl')
    print("\n✅ TF-IDF model trained and saved!")


if __name__ == "__main__":
    train_tfidf_baseline()