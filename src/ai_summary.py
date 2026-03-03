from config import Config
from src.logger import setup_logger
from google import genai
from dotenv import load_dotenv


load_dotenv()
logger = setup_logger(__name__)

class AIPrompter:    
    def __init__(self, api_key=None):
        self.enabled = False
        self.client = None

        try:
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                self.client = genai.Client()

            self.enabled = True
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {str(e)}. AI summaries will be disabled.")
            self.enabled = False
            
    def generate_summary(self, prediction_text, confidence, top_features):
        if prediction_text == "NORMAL":
            logger.debug(f"Skipping AI summary for NORMAL prediction (confidence: {confidence:.2f}%)")
            return f"✅ Network traffic appears normal with {confidence:.2f}% confidence."
        
        try:
            if not self.enabled:
                return self._fallback_summary(prediction_text, confidence, top_features)
            
            top_features_str = ", ".join(
                [f"{feat}: {val:.3f}" for feat, val in top_features]
            )

            prompt = f"""
            You are an experienced security analyst in an organisation.

            Based on the intrusion detection analysis:
            - Prediction: {prediction_text}
            - Confidence: {confidence:.2f}%
            - Top contributing features (SHAP values): {top_features_str}
            
            Provide a concise, professional security analysis (2-3 sentences max):
1. What type of attack this might be
2. Why these features indicate an attack
3. Recommended action
            """

            response = self.client.models.generate_content(model=Config.GEMINI_MODEL, contents=prompt)
            
            if response and hasattr(response, 'text') and response.text:
                summary = response.text.strip()
                logger.debug(f"AI summary generated successfully")
                return summary
            else:
                logger.warning(f"AI summary generation failed: {str(e)}")
                return self._fallback_summary(prediction_text, confidence, top_features)
            
        except Exception as e:
            logger.warning(f"AI generation failed: {str(e)}")
            return self._fallback_summary(prediction_text, confidence, top_features)
    
    def _fallback_summary(prediction_text, confidence, top_features):
        try:
            features_str = ", ".join([f"{f}: {v:.3f}" for f, v in top_features])
        except Exception as e:
            logger.error(f"Error formatting features: {str(e)}")
            features_str = "N/A"
        
        return (f"Model predicts {prediction_text} with {confidence:.2f}% confidence. "
                f"Top contributing features: {features_str}")