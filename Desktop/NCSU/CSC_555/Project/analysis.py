import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import logging
from datetime import datetime

# Configure logging
log_filename = f'twitter_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Read the relevant data files from the 'cleaned-data' folder
logger.info("Loading cleaned data files...")
try:
    tweets_df = pd.read_csv('./cleaned-data/cleaned_tweet_metadata.csv')
    users_df = pd.read_csv('./cleaned-data/cleaned_twitter_user.csv')
    logger.info(f"Loaded {len(tweets_df)} tweets and {len(users_df)} user records")
except Exception as e:
    logger.error(f"Error loading cleaned data files: {str(e)}")
    raise

# Merge tweet and user data
logger.info("Merging tweet and user data...")
tweets_users_df = tweets_df.merge(
    users_df,
    left_on='author_id',
    right_on='id',
    suffixes=('_tweet', '_user')
)

# Analyze Interaction Data for Tweets
logger.info("Analyzing tweet interaction data...")
interaction_metrics = [
    'retweet_count',
    'favorite_count',
    'quote_count',
    'reply_count',
    'followers_count'
]

# Ensure the interaction metrics are numeric
for metric in interaction_metrics:
    tweets_users_df[metric] = pd.to_numeric(tweets_users_df[metric], errors='coerce')

# Remove rows with NaN in interaction metrics
tweets_users_df.dropna(subset=interaction_metrics, inplace=True)

# Plot the distribution of interaction metrics with increased granularity
plt.figure(figsize=(18, 10))
for i, metric in enumerate(interaction_metrics):
    plt.subplot(2, 3, i + 1)
    # Increase bins and use log scale if necessary
    max_value = tweets_users_df[metric].max()
    if max_value > 1000:
        sns.histplot(tweets_users_df[metric], bins=50, kde=True, log_scale=(True, False))
        plt.xlabel(f'{metric} (Log Scale)')
    else:
        sns.histplot(tweets_users_df[metric], bins=50, kde=True)
        plt.xlabel(metric)
    plt.title(f'Distribution of {metric}')
plt.tight_layout()
plt.savefig('interaction_metrics_distribution.png')
logger.info("Saved interaction metrics distribution plot.")

# Analyze Popular Users with Increased Granularity
logger.info("Identifying popular users with increased granularity...")
# Define threshold for popular users (e.g., top 10% by followers_count)
popularity_threshold = tweets_users_df['followers_count'].quantile(0.90)
popular_users_df = tweets_users_df[tweets_users_df['followers_count'] >= popularity_threshold]

logger.info(f"Number of popular users: {popular_users_df['author_id'].nunique()}")

# Metrics for popular users
popular_user_metrics = popular_users_df.groupby('author_id')[interaction_metrics].mean()
popular_user_metrics.reset_index(inplace=True)

# Sort users by followers_count
popular_user_metrics.sort_values(by='followers_count', ascending=False, inplace=True)

# Plot average interaction metrics for popular users
plt.figure(figsize=(14, 8))
# Plot each metric separately
for metric in interaction_metrics[:-1]:  # Exclude 'followers_count' from metrics to plot
    sns.lineplot(
        data=popular_user_metrics,
        x='author_id',
        y=metric,
        label=metric
    )

plt.title('Interaction Metrics for Popular Users')
plt.xlabel('Author ID')
plt.ylabel('Average Metric Value')
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.savefig('popular_users_interaction_metrics.png')
logger.info("Saved popular users interaction metrics plot.")

# Tune the limits
plt.xlim(0, 50)  # Adjust to show top 50 popular users
plt.ylim(bottom=0)  # Ensure y-axis starts at 0
plt.savefig('popular_users_interaction_metrics_limited.png')
logger.info("Saved limited popular users interaction metrics plot.")

# Analyze Users with Minimal Impact Who Were Censored with Increased Granularity
logger.info("Analyzing users with minimal impact who were censored...")
# Define threshold for minimal impact users (e.g., bottom 10% by followers_count)
minimal_impact_threshold = tweets_users_df['followers_count'].quantile(0.10)
minimal_impact_censored_users = tweets_users_df[
    (tweets_users_df['followers_count'] <= minimal_impact_threshold) &
    (tweets_users_df['protected'] == True)
]

num_censored_users = minimal_impact_censored_users['author_id'].nunique()
logger.info(f"Number of censored users with minimal impact: {num_censored_users}")

if num_censored_users > 0:
    censored_user_metrics = minimal_impact_censored_users.groupby('author_id')[interaction_metrics].mean()
    censored_user_metrics.reset_index(inplace=True)
    censored_user_metrics.sort_values(by='followers_count', ascending=False, inplace=True)
    
    # Plot interaction metrics for censored users
    plt.figure(figsize=(14, 8))
    for metric in interaction_metrics[:-1]:
        sns.lineplot(
            data=censored_user_metrics,
            x='author_id',
            y=metric,
            label=metric
        )
    
    plt.title('Interaction Metrics for Censored Users with Minimal Impact')
    plt.xlabel('Author ID')
    plt.ylabel('Average Metric Value')
    plt.xticks(rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.savefig('censored_users_interaction_metrics.png')
    logger.info("Saved censored users interaction metrics plot.")
else:
    logger.info("No censored users with minimal impact found.")

# Additional Visualization: Correlation Heatmap
logger.info("Generating correlation heatmap of interaction metrics...")
correlation_matrix = tweets_users_df[interaction_metrics].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='Blues')
plt.title('Correlation Heatmap of Interaction Metrics')
plt.tight_layout()
plt.savefig('interaction_metrics_correlation_heatmap.png')
logger.info("Saved interaction metrics correlation heatmap.")

# Save the summary statistics to CSV
interaction_summary = tweets_users_df[interaction_metrics].describe()
interaction_summary.to_csv('interaction_summary.csv')
popular_user_metrics.to_csv('popular_user_metrics.csv', index=False)
if num_censored_users > 0:
    censored_user_metrics.to_csv('censored_user_metrics.csv', index=False)

logger.info("Analysis completed successfully.")