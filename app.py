from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import joblib
import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from src.logger import setup_logger
from src.validators import validate_file_upload, validate_input_data
from src.explainer import SHAPExplainerManager
from src.ai_summary import AIPrompter


app = Flask(__name__)
app.config.from_object(Config)

logger = setup_logger(__name__)


try:
    model_path = os.path.join(os.path.dirname(__file__), Config.MODEL_PATH)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model = joblib.load(model_path)
    preprocessor = model.named_steps['preprocess']
    clf = model.named_steps['clf']
    
    shap_manager = SHAPExplainerManager(clf)
    ai_prompter = AIPrompter(api_key=Config.GEMINI_API_KEY)
    
    logger.info("Model loaded successfully")
except Exception as e:
    logger.critical(f"Failed to load model: {str(e)}")
    raise

categorical_features = ['protocol_type', 'service', 'flag']
numeric_features = [
    'duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
    'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted',
    'num_root', 'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds',
    'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
    'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
]

# Home page with form
@app.route('/', methods=['GET'])
def index():
    """Home page with upload form."""
    logger.info(f"Index page requested from {request.remote_addr}")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle predictions."""
    """ The user can submit a CSV file containing one or more rows of features."""
    logger.info(f"Prediction request from {request.remote_addr}")

    try:
        # Validate file...
        file = request.files.get('data_file')
        file_error = validate_file_upload(file)

        if file_error:
            logger.warning(f"File validation failed: {file_error}")
            return render_template('error.html', error=file_error), 400

        # Read CSV...
        try:
            input_df = pd.read_csv(file)
            logger.info(f"CSV loaded: {len(input_df)} rows")
        except Exception as e:
            error_msg = f"Error reading CSV: {str(e)}"
            logger.error(error_msg)
            return render_template('error.html', error=error_msg), 400

        # Validate data...
        validation_errors = validate_input_data(input_df, numeric_features, categorical_features)
        
        if validation_errors:
            error_msg = "\n".join(validation_errors)
            logger.warning(f"Data validation failed: {error_msg}")
            return render_template('error.html', error=error_msg), 400
        
        # Make predictions...
        logger.info(f"Processing {len(input_df)} rows")
        preds = model.predict(input_df)
        pred_probas = model.predict_proba(input_df)

        # Get SHAP values...
        input_preprocessed = preprocessor.transform(input_df)
        explainer = shap_manager.get_explainer()
        shap_vals = explainer.shap_values(input_preprocessed)

        # Handle binary classification SHAP format...
        if len(shap_vals.shape) == 3:
            shap_vals = shap_vals[1]
        
        # Get feature names...
        cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
        all_feature_names = np.concatenate([numeric_features, cat_feature_names])

        # Process results...
        results = []
        for i, row in input_df.iterrows():
            prediction = int(preds[i])
            confidence = float(pred_probas[i][prediction] * 100)
            single_shap = shap_vals[i]
            shap_dict = dict(zip(all_feature_names, single_shap))
            top_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            
            # Generate AI summary...
            prediction_text = "ATTACK" if prediction == 1 else "NORMAL"
            ai_summary = ai_prompter.generate_summary(prediction_text, confidence, top_features)
            
            results.append({
                'data': row.to_dict(),
                'prediction': prediction,
                'confidence': confidence,
                'shap_values': top_features,
                'ai_summary': ai_summary
            })
        
        logger.info(f"Prediction completed: {len(results)} results")
        return render_template('result.html', results=results)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return render_template('error.html', error="An unexpected error occurred"), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(error)}", exc_info=True)
    return render_template('error.html', error="Internal server error"), 500


if __name__ == '__main__':
    app.run(debug=True)
