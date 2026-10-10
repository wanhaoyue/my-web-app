import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from textblob import TextBlob

# Configure stdout logging for AWS CloudWatch
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")

@app.route("/")
def index():
    """Renders the frontend UI for customers."""
    return render_template("index.html", version=APP_VERSION)

@app.route("/api/sentiment", methods=["POST"])
def analyze_sentiment():
    """API endpoint to process customer text and return sentiment metrics."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text cannot be empty"}), 400

    try:
        # Run sentiment analysis using TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity     # Range: -1.0 (very negative) to 1.0 (very positive)
        subjectivity = blob.sentiment.subjectivity # Range: 0.0 (objective) to 1.0 (subjective)

        # Categorize polarity
        if polarity > 0.1:
            sentiment = "Positive"
            badge_color = "success"
        elif polarity < -0.1:
            sentiment = "Negative"
            badge_color = "danger"
        else:
            sentiment = "Neutral"
            badge_color = "secondary"

        logger.info(f"Analyzed text successfully. Sentiment: {sentiment} (Polarity: {polarity})")

        return jsonify({
            "status": "success",
            "sentiment": sentiment,
            "badge_color": badge_color,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3)
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return jsonify({"error": "Internal processing error"}), 500

@app.route("/health")
def health():
    """Health check endpoint for ECS Target Groups."""
    return jsonify({"status": "healthy", "version": APP_VERSION}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)