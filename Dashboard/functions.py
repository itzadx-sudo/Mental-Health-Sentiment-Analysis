import pandas as pd
import os
from collections import Counter
import re
from textblob import TextBlob
import nltk
import ssl

# NLTK Stopwords Loader
from nltk.corpus import stopwords

try:
    # Attempt to load stopwords directly (if already downloaded)
    stop_words = set(stopwords.words('english'))
except LookupError:
    # If stopwords are not found, attempt to download them
    print("NLTK 'stopwords' corpus not found. Attempting download...")
    try:
        nltk.download('stopwords', quiet=True)
    except Exception as e:
        # If standard download fails (e.g., SSL error), disable SSL verification and retry
        print(f"Standard download failed: {e}. Trying again with SSL verification disabled.")
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass  # Handle older Python versions
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        # Retry download with SSL verification disabled
        nltk.download('stopwords', quiet=True)

    # Attempt to load the stopwords again after download attempt
    try:
        stop_words = set(stopwords.words('english'))
        print("NLTK 'stopwords' loaded successfully.")
    except LookupError:
        # If loading still fails, create an empty set and warn the user
        print("FATAL: Could not load 'stopwords' even after download attempt.")
        print("Text analysis features may not work correctly.")
        stop_words = set()


def load_data():
    # loads and automatically cleans the dataset by searching in common pre-defined relative paths.
    filename = "Combined Data.csv"
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # List of paths to try, in order of priority
    potential_paths = [
        os.path.join(script_dir, 'Source Data', filename)]

    df = None
    found_path = None

    print("Searching for 'Combined Data.csv'...")

    for path in potential_paths:
        # Normalize path for consistent checking
        norm_path = os.path.normpath(path)

        if os.path.exists(norm_path):
            try:
                df = pd.read_csv(norm_path)
                found_path = norm_path
                break  # Stop searching once the file is successfully loaded
            except Exception as e:
                print(f"Found file at {norm_path}, but failed to read: {e}")

    # If loop finishes without finding and loading the file
    if df is None:
        print("Could not find 'Combined Data.csv'.")
        return None, "File not found"

    # Data Cleaning

    # Rename 'status' to 'label' if 'label' doesn't exist
    if 'status' in df.columns and 'label' not in df.columns:
        df = df.rename(columns={'status': 'label'})
    elif 'label' not in df.columns:
        print("Warning: No 'status' or 'label' column found in the raw data.")

    print("CLEANING DATA...")
    original_rows = len(df)

    # Drop duplicates and rows with missing values
    df = df.drop_duplicates()
    df = df.dropna()

    # Ensure 'statement' column has content
    if 'statement' in df.columns:
        df = df[df['statement'].astype(str).str.strip().str.len() > 0]

    # Reset index after dropping rows
    df = df.reset_index(drop=True)

    if original_rows > 0:
        pass
    else:
        print("CLEANING COMPLETE! No data to process.")

    return df, found_path


def get_sentiment(polarity):
    # Categorizes a polarity score into 'positive', 'negative', or 'neutral'.
    if polarity > 0.05:
        return 'positive'
    elif polarity < -0.05:
        return 'negative'
    else:
        return 'neutral'


def process_data(df, max_word_len=500):
    # Enriches the DataFrame with sentiment analysis and text metrics.
    if df is None:
        return None

    if 'word_len' not in df.columns:
        if 'statement' in df.columns:
            df['word_len'] = df['statement'].astype(str).apply(lambda x: len(x.split()))
        else:
            df['word_len'] = 0

    if 'char_len' not in df.columns:
        if 'statement' in df.columns:
            df['char_len'] = df['statement'].astype(str).apply(len)
        else:
            df['char_len'] = 0

    clean_df = df[df['word_len'] <= max_word_len].copy().reset_index(drop=True)

    if 'statement' in clean_df.columns:
        print("Preparing your Dashboard...")
        try:
            analysis = clean_df['statement'].astype(str).apply(lambda text: TextBlob(text).sentiment)
            clean_df['polarity'] = analysis.apply(lambda x: x.polarity)
            clean_df['subjectivity'] = analysis.apply(lambda x: x.subjectivity)
            clean_df['sentiment'] = clean_df['polarity'].apply(get_sentiment)
            clean_df['sentiment_score'] = clean_df['polarity']
            print("Launching Dashboard...")
        except Exception as e:
            print(f"Error during sentiment analysis: {e}. Filling with defaults.")
            clean_df['polarity'] = 0.0
            clean_df['subjectivity'] = 0.0
            clean_df['sentiment'] = 'neutral'
            clean_df['sentiment_score'] = 0.0
    else:
        print("Warning: 'statement' column not found. Skipping sentiment analysis.")
        clean_df['polarity'] = 0.0
        clean_df['subjectivity'] = 0.0
        clean_df['sentiment'] = 'neutral'
        clean_df['sentiment_score'] = 0.0

    return clean_df


def clean_text_for_freq(text):
    # Prepares text for frequency analysis (lowercase, remove URLs, non-letters, stopwords).
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    words = [w for w in text.split() if w not in stop_words]
    return words


def get_word_frequency(df, category='all', top_n=20):
    # Calculates the top N most frequent words for a given category.
    if category != 'all':
        texts = df[df['label'] == category]['statement'].astype(str)
    else:
        texts = df['statement'].astype(str)

    all_words = []
    for text in texts:
        words = clean_text_for_freq(text)
        all_words.extend(words)

    word_freq = Counter(all_words).most_common(top_n)
    return pd.DataFrame(word_freq, columns=['word', 'frequency'])


def get_bigram_frequency(df, category='all', top_n=15):
    # Calculates the top N most frequent bigrams (word pairs) for a given category.
    if category != 'all':
        texts = df[df['label'] == category]['statement'].astype(str)
    else:
        texts = df['statement'].astype(str)

    all_bigrams = []
    for text in texts:
        words = clean_text_for_freq(text)
        bigrams = [f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)]
        all_bigrams.extend(bigrams)

    bigram_freq = Counter(all_bigrams).most_common(top_n)
    return pd.DataFrame(bigram_freq, columns=['bigram', 'frequency'])


def calculate_statistics(df):
    # Calculates a dictionary of key statistics for a given DataFrame.
    if df is None or df.empty:
        return {
            'total_rows': 0, 'avg_word_len': 0, 'avg_char_len': 0,
            'max_word_len': 0, 'median_word_len': 0, 'median_char_len': 0,
            'num_categories': 0, 'avg_polarity': 0, 'avg_subjectivity': 0,
            'positive_count': 0, 'negative_count': 0, 'neutral_count': 0
        }

    avg_word_len = df['word_len'].mean() if 'word_len' in df.columns else 0
    avg_char_len = df['char_len'].mean() if 'char_len' in df.columns else 0
    max_word_len = df['word_len'].max() if 'word_len' in df.columns else 0
    median_word_len = df['word_len'].median() if 'word_len' in df.columns else 0
    median_char_len = df['char_len'].median() if 'char_len' in df.columns else 0
    avg_polarity = df['polarity'].mean() if 'polarity' in df.columns else 0
    avg_subjectivity = df['subjectivity'].mean() if 'subjectivity' in df.columns else 0

    stats = {
        'total_rows': df.shape[0],
        'avg_word_len': avg_word_len,
        'avg_char_len': avg_char_len,
        'max_word_len': max_word_len,
        'median_word_len': median_word_len,
        'median_char_len': median_char_len,
        'num_categories': df['label'].nunique() if 'label' in df.columns else 0,
        'avg_polarity': avg_polarity,
        'avg_subjectivity': avg_subjectivity,
    }

    if 'sentiment' in df.columns:
        sentiment_counts = df['sentiment'].value_counts()
        stats['positive_count'] = sentiment_counts.get('positive', 0)
        stats['negative_count'] = sentiment_counts.get('negative', 0)
        stats['neutral_count'] = sentiment_counts.get('neutral', 0)
    else:
        stats['positive_count'] = 0
        stats['negative_count'] = 0
        stats['neutral_count'] = 0

    return stats