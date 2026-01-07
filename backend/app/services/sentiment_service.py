"""Sentiment analysis service using transformers"""
import logging
from typing import Dict, Any, Optional, List
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis for financial news using pre-trained models"""

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize sentiment analyzer

        Args:
            model_name: HuggingFace model name (default: finbert for financial text)
        """
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1

        logger.info(f"Loading sentiment model: {model_name}")
        logger.info(f"Using device: {'GPU' if self.device == 0 else 'CPU'}")

        try:
            # Load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Create pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
                max_length=512,
                truncation=True
            )

            logger.info("Sentiment analyzer loaded successfully")

        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            raise

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis results
        """
        if not text or len(text.strip()) == 0:
            return {
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'normalized_score': 0.0
            }

        try:
            # Run sentiment analysis
            result = self.sentiment_pipeline(text[:512])[0]  # Limit to 512 tokens

            # Extract label and score
            label = result['label'].lower()
            confidence = float(result['score'])

            # Normalize score to -1 to 1 range
            if label == 'positive':
                normalized_score = confidence
            elif label == 'negative':
                normalized_score = -confidence
            else:  # neutral
                normalized_score = 0.0

            return {
                'label': label,
                'score': confidence,
                'confidence': confidence,
                'normalized_score': normalized_score
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'normalized_score': 0.0,
                'error': str(e)
            }

    def analyze_article(
        self,
        title: str,
        description: Optional[str] = None,
        content: Optional[str] = None,
        title_weight: float = 0.4,
        description_weight: float = 0.35,
        content_weight: float = 0.25
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of news article with weighted components

        Args:
            title: Article title
            description: Article description
            content: Article content
            title_weight: Weight for title sentiment
            description_weight: Weight for description sentiment
            content_weight: Weight for content sentiment

        Returns:
            Dictionary with overall sentiment analysis
        """
        sentiments = []
        weights = []

        # Analyze title
        if title:
            title_sentiment = self.analyze_text(title)
            sentiments.append(title_sentiment)
            weights.append(title_weight)

        # Analyze description
        if description:
            desc_sentiment = self.analyze_text(description)
            sentiments.append(desc_sentiment)
            weights.append(description_weight)

        # Analyze content (first 512 chars)
        if content:
            content_preview = content[:512]
            content_sentiment = self.analyze_text(content_preview)
            sentiments.append(content_sentiment)
            weights.append(content_weight)

        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        # Calculate weighted average
        weighted_score = sum(
            s['normalized_score'] * w
            for s, w in zip(sentiments, normalized_weights)
        )

        weighted_confidence = sum(
            s['confidence'] * w
            for s, w in zip(sentiments, normalized_weights)
        )

        # Determine overall label
        if weighted_score > 0.15:
            overall_label = 'positive'
        elif weighted_score < -0.15:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'

        return {
            'label': overall_label,
            'score': weighted_score,
            'confidence': weighted_confidence,
            'normalized_score': weighted_score,
            'components': {
                'title': sentiments[0] if len(sentiments) > 0 else None,
                'description': sentiments[1] if len(sentiments) > 1 else None,
                'content': sentiments[2] if len(sentiments) > 2 else None
            }
        }

    def analyze_batch(self, texts: List[str], batch_size: int = 8) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple texts in batches

        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing

        Returns:
            List of sentiment analysis results
        """
        results = []

        try:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_results = self.sentiment_pipeline(batch)

                for result in batch_results:
                    label = result['label'].lower()
                    confidence = float(result['score'])

                    if label == 'positive':
                        normalized_score = confidence
                    elif label == 'negative':
                        normalized_score = -confidence
                    else:
                        normalized_score = 0.0

                    results.append({
                        'label': label,
                        'score': confidence,
                        'confidence': confidence,
                        'normalized_score': normalized_score
                    })

        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {e}")
            # Return neutral results for all texts on error
            results = [
                {
                    'label': 'neutral',
                    'score': 0.0,
                    'confidence': 0.0,
                    'normalized_score': 0.0,
                    'error': str(e)
                }
                for _ in texts
            ]

        return results

    def get_sentiment_summary(self, sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for a list of sentiments

        Args:
            sentiments: List of sentiment analysis results

        Returns:
            Summary statistics
        """
        if not sentiments:
            return {
                'avg_score': 0.0,
                'median_score': 0.0,
                'std_score': 0.0,
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'total_count': 0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0
            }

        scores = [s['normalized_score'] for s in sentiments]
        labels = [s['label'] for s in sentiments]

        positive_count = labels.count('positive')
        neutral_count = labels.count('neutral')
        negative_count = labels.count('negative')
        total_count = len(sentiments)

        return {
            'avg_score': float(np.mean(scores)),
            'median_score': float(np.median(scores)),
            'std_score': float(np.std(scores)),
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'total_count': total_count,
            'positive_ratio': positive_count / total_count if total_count > 0 else 0.0,
            'negative_ratio': negative_count / total_count if total_count > 0 else 0.0
        }


# Global instance (lazy loaded)
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create global sentiment analyzer instance"""
    global _sentiment_analyzer

    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()

    return _sentiment_analyzer
