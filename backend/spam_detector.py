#!/usr/bin/env python3
"""
Local machine-learning spam detector for Vishakha_Notewise.

This module downloads a public SMS spam dataset once, trains four classic
scikit-learn models, and exposes a single predict_all(text) function that
compares how each model classifies the same message.
"""

import math
import os
from collections import Counter

import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

DATA_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spam.tsv')
RANDOM_STATE = 42


def _ensure_dataset_exists():
    """
    Download the SMS spam dataset once and store it in the project root.

    Keeping a local copy means the project does not need to re-download the
    dataset every time Flask starts.
    """
    if os.path.exists(DATA_PATH):
        return

    print(f"[SpamDetector] Downloading dataset to {DATA_PATH} ...")
    response = requests.get(DATA_URL, timeout=30)
    response.raise_for_status()

    with open(DATA_PATH, "wb") as dataset_file:
        dataset_file.write(response.content)


def _load_dataset():
    """
    Load the dataset into a DataFrame.

    The SMS Spam Collection contains two columns:
    - label: 'spam' or 'ham'
    - text: the actual SMS message
    """
    _ensure_dataset_exists()
    dataset = pd.read_csv(DATA_PATH, sep="\t", header=None, names=["label", "text"])
    dataset["text"] = dataset["text"].fillna("").astype(str)
    dataset["label"] = dataset["label"].fillna("ham").astype(str)
    return dataset


def _build_models():
    """
    Create the four models used in this project.

    Each model learns in a different way, which makes comparison useful for
    understanding machine learning:
    - MultinomialNB: counts word evidence and estimates the probability that a
      message belongs to the spam class.
    - LogisticRegression: learns a mathematical decision boundary between spam
      and normal messages.
    - LinearSVC: finds the widest possible margin separating spam from ham.
    - RandomForestClassifier: combines many decision trees and takes a vote.
    """
    return {
        "Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Support Vector Machine": LinearSVC(random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
    }


def _round_percent(value):
    """Convert a ratio to a percentage rounded to one decimal place."""
    return round(float(value) * 100, 1)


def _decision_score_to_confidence(model, feature_vector, predicted_label):
    """
    Convert model output into an easy-to-read confidence percentage.

    Confidence answers the question:
    "How strongly does this model believe its prediction?"

    Models that support predict_proba() already return probabilities directly.
    LinearSVC does not return probabilities by default, so we convert its
    distance-from-boundary score into a probability-like value using a sigmoid.
    """
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(feature_vector)[0]
        class_index = list(model.classes_).index(predicted_label)
        return round(float(probabilities[class_index]) * 100, 1)

    if hasattr(model, "decision_function"):
        decision_value = model.decision_function(feature_vector)
        if hasattr(decision_value, "__len__"):
            score = float(decision_value[0])
        else:
            score = float(decision_value)

        spam_probability = 1.0 / (1.0 + math.exp(-score))
        if predicted_label == "spam":
            return round(spam_probability * 100, 1)
        return round((1.0 - spam_probability) * 100, 1)

    return 50.0


def _train_models_once():
    """
    Train all models a single time when the module is imported.

    TF-IDF vectorization transforms each message into a numeric feature vector.
    It gives high weight to words that are important in a message but not overly
    common across every message in the dataset. This helps the models focus on
    informative words such as "free", "win", or "claim" instead of very common
    words like "the" or "is".

    The accuracy we compute here shows how many messages each model classified
    correctly on the held-out test set. Even though the modal labels it as
    "Training Accuracy", it is really an evaluation score that tells us how well
    the trained model generalizes to unseen examples.
    """
    dataset = _load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        dataset["text"],
        dataset["label"],
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=dataset["label"]
    )

    vectorizer = TfidfVectorizer(stop_words="english")
    X_train_features = vectorizer.fit_transform(X_train)
    X_test_features = vectorizer.transform(X_test)

    trained_models = {}
    accuracies = {}

    for model_name, model in _build_models().items():
        model.fit(X_train_features, y_train)
        predictions = model.predict(X_test_features)
        trained_models[model_name] = model
        accuracies[model_name] = _round_percent(accuracy_score(y_test, predictions))

    accuracy_message = ", ".join(
        f"{model_name}: {score:.1f}%"
        for model_name, score in accuracies.items()
    )
    print(f"[SpamDetector] Models trained successfully. Accuracies: {accuracy_message}")

    return vectorizer, trained_models, accuracies


VECTORIZER, TRAINED_MODELS, MODEL_ACCURACIES = _train_models_once()


def predict_all(text):
    """
    Run the same text through all four spam-detection models.

    Args:
        text (str): The message to classify.

    Returns:
        dict: Majority-vote verdict plus one result object per model.
    """
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise ValueError("Text is required for spam detection.")

    feature_vector = VECTORIZER.transform([cleaned_text])
    results = []
    votes = []

    for model_name, model in TRAINED_MODELS.items():
        predicted_label = str(model.predict(feature_vector)[0])
        confidence = _decision_score_to_confidence(model, feature_vector, predicted_label)

        results.append({
            "model": model_name,
            "verdict": predicted_label,
            "confidence": confidence,
            "accuracy": MODEL_ACCURACIES[model_name],
        })
        votes.append(predicted_label)

    vote_counter = Counter(votes)
    overall_verdict = "spam" if vote_counter["spam"] > vote_counter["ham"] else "ham"

    return {
        "overall_verdict": overall_verdict,
        "results": results
    }
