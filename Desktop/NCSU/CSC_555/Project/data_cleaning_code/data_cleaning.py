import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'data_cleaning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

def clean_user_data(df):
    """Clean Twitter user data"""
    # Convert dates to datetime
    date_columns = ['created_at', 'access']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    # Clean boolean columns
    bool_columns = ['protected', 'verified', 'default_profile', 'default_profile_image']
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).map({'True': True, 'False': False})
    # Clean numeric columns
    numeric_columns = ['followers_count', 'friends_count', 'favourites_count', 'listed_count', 'statuses_count']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def clean_tweet_data(df):
    """Clean tweet metadata"""
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    engagement_cols = ['retweet_count', 'favorite_count', 'quote_count', 'reply_count']
    for col in engagement_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def clean_network_data(df):
    """Clean network interaction data"""
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    id_columns = [col for col in df.columns if 'id' in col.lower()]
    for col in id_columns:
        df[col] = df[col].astype(str)
    return df

def clean_all_files():
    """Clean all CSV files in write-folder and save to cleaned-data"""
    input_dir = 'write-folder'
    output_dir = 'cleaned-data'  # Updated output directory

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each CSV file
    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f'cleaned_{filename}')

        try:
            logging.info(f"Processing {filename}")
            # Read CSV
            df = pd.read_csv(input_path, low_memory=False)
            original_shape = df.shape

            # Apply appropriate cleaning based on file type
            if 'user' in filename.lower():
                df = clean_user_data(df)
            elif 'tweet' in filename.lower():
                df = clean_tweet_data(df)
            elif 'network' in filename.lower():
                df = clean_network_data(df)

            # General cleaning for all files
            df = df.drop_duplicates()
            df = df.dropna(how='all')
            str_columns = df.select_dtypes(include=['object']).columns
            for col in str_columns:
                df[col] = df[col].str.strip()

            # Log cleaning results
            cleaned_shape = df.shape
            rows_removed = original_shape[0] - cleaned_shape[0]
            logging.info(f"Cleaned {filename}: removed {rows_removed} rows")

            # Save cleaned file
            df.to_csv(output_path, index=False)
            logging.info(f"Saved cleaned file to {output_path}")

        except Exception as e:
            logging.error(f"Error processing {filename}: {str(e)}")
            continue

if __name__ == "__main__":
    try:
        logging.info("Starting data cleaning process")
        clean_all_files()
        logging.info("Data cleaning completed successfully")
    except Exception as e:
        logging.error(f"Data cleaning failed: {str(e)}")