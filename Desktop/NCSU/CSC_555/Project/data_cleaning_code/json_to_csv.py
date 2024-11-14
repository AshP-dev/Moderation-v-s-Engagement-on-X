import os
import json
import csv

def extract_tweet_data(tweet):
    """Extract selected fields from a tweet JSON object."""
    tweet_data = {
        'created_at': tweet.get('created_at'),
        'id': tweet.get('id'),
        'text': tweet.get('text'),
        'user_id': tweet.get('user', {}).get('id'),
        'user_screen_name': tweet.get('user', {}).get('screen_name'),
    }
    return tweet_data

def convert_json_to_csv(input_folder, output_folder):
    """Convert JSON files in the input folder to CSV and save them in the output folder without creating empty CSV files."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace('.json', '.csv'))

            try:
                with open(input_path, 'r', encoding='utf-8') as file:
                    tweets = []
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            tweet_json = json.loads(line)
                            tweet_data = extract_tweet_data(tweet_json)
                            tweets.append(tweet_data)
                        except json.JSONDecodeError as e:
                            print(f'Error decoding JSON in file {filename}: {e}')
                            continue

                if tweets:
                    fieldnames = tweets[0].keys()
                    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(tweets)
                    print(f'Converted {filename} to CSV and saved to {output_path}')
                else:
                    print(f'No valid tweets found in {filename}. Skipping CSV generation.')
            except Exception as e:
                print(f'An error occurred while processing file {filename}: {e}')

if __name__ == "__main__":
    input_folder = '/Users/ashwatthaphatak/Desktop/NCSU/CSC_555/Project/data/Output'      # Replace with the path to your JSON folder
    output_folder = '/Users/ashwatthaphatak/Desktop/NCSU/CSC_555/Project/data/converted_from_json'
    convert_json_to_csv(input_folder, output_folder)