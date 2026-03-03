import shap
from src.logger import setup_logger

logger = setup_logger(__name__)

class SHAPExplainerManager:    
    def __init__(self, model):
        self.model = model
        self.explainer = None
    
    def get_explainer(self):
        if self.explainer is None:
            try:
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("SHAP explainer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SHAP: {str(e)}")
                raise
            
        return self.explainer
