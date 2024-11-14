import os
import pandas as pd

def delete_empty_csv_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            try:
                df = pd.read_csv(file_path)
                if df.empty:
                    os.remove(file_path)
                    print(f'Deleted empty file: {filename}')
            except pd.errors.EmptyDataError:
                os.remove(file_path)
                print(f'Deleted empty file: {filename}')
            except Exception as e:
                print(f'Error processing file {filename}: {e}')

if __name__ == "__main__":
    folder_path = '/Users/ashwatthaphatak/Desktop/NCSU/CSC_555/Project/data/converted_from_json'  # Replace with your folder path if different
    delete_empty_csv_files(folder_path)