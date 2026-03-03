import pandas as pd
from config import Config


def validate_file_upload(file):
    """
    Validate uploaded file.
    
    Returns:
        str: Error message if validation fails, None otherwise
    """
    if not file:
        return "No file uploaded"
    
    if file.filename == '':
        return "No file selected"

    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        return f"Only {', '.join(Config.ALLOWED_EXTENSIONS)} files allowed"

    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > Config.MAX_FILE_SIZE:
        max_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
        return f"File size exceeds {max_mb:.1f}MB limit"
    
    return None

def validate_input_data(input_df, numeric_features, categorical_features):
    """
    Validate input dataframe.
    
    Returns:
        list: List of error messages, empty if valid
    """
    errors = []
    
    # Check empty dataframe...
    if input_df.empty:
        errors.append("CSV file is empty")
        return errors
    
    # Check required columns...
    required_cols = set(numeric_features + categorical_features)
    missing_cols = required_cols - set(input_df.columns)
    if missing_cols:
        errors.append(f"Missing columns: {', '.join(missing_cols)}")
        return errors
    
    # Check row count...
    if len(input_df) > Config.MAX_ROWS:
        errors.append(f"Maximum {Config.MAX_ROWS} rows allowed. Found {len(input_df)}")
    
    # Validate numeric columns...
    for col in numeric_features:
        if col in input_df.columns:
            input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
            if input_df[col].isna().any():
                bad_count = input_df[col].isna().sum()
                errors.append(f"Column '{col}' has {bad_count} non-numeric values")
    
    return errors