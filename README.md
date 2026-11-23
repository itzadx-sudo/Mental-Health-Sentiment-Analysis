# Mental Health Sentiment Analysis Dashboard

An interactive web dashboard for analyzing sentiment patterns in social media posts related to mental health conditions. Built with Python and Dash, it helps researchers, policymakers, and mental health organizations detect trends and derive actionable insights from mental health discussions.

## Overview

This project processes 51,192 social media statements across seven categories (Anxiety, Depression, Stress, Bipolar, Suicidal, Personality disorder, and Normal) to surface sentiment trends, word patterns, and statistical summaries through a visually rich, multi-page dashboard.

## Features

- **Overview** — Project summary and key dataset metrics
- **Metrics** — Statistical breakdown of word length, subjectivity, and category distribution
- **Sentiment Analysis** — Polarity distribution, intensity, emotional complexity, and treemap views
- **Text Analysis** — Word frequency and bigram analysis per category (with interactive filtering)
- **Data Explorer** — Paginated raw data browser (50 records per page)
- **Results** — Summary findings and links to mental health resources

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Dash |
| Visualizations | Plotly |
| Data Processing | Pandas |
| Sentiment Analysis | TextBlob |
| NLP Preprocessing | NLTK |
| Styling | Custom CSS (Glassmorphism) |

## Dataset

- **Source:** [Kaggle — Sentiment Analysis for Mental Health](https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health)
- **Size:** ~31 MB, 53,043 raw records; the dashboard analyses 51,192 after dropping empty rows and posts over 500 words
- **Columns:** `statement` (post text), `status` (mental health category)
- **Categories:** Anxiety, Depression, Suicidal, Bipolar, Stress, Normal, Personality Disorder

## Project Structure

```
Mental-Health-Sentiment-Analysis/
├── Dashboard/
│   ├── Source Data/
│   │   └── Combined Data.csv
│   ├── app.py              # Main Dash application and layout
│   ├── functions.py        # Data loading, NLP, and sentiment processing
│   ├── visualizations.py   # Plotly chart builders
│   └── design.py           # CSS stylesheet (glassmorphism theme)
└── User Guide/
    └── User Guide.docx
```

## Installation & Setup

**Prerequisites:** Python 3.7+

```bash
# 1. Clone the repository
git clone https://github.com/itzadx-sudo/mental-health-sentiment-analysis.git
cd mental-health-sentiment-analysis

# 2. Install dependencies
pip install dash plotly pandas textblob nltk dash-iconify

# 3. Run the application
cd Dashboard
python app.py
```

Open your browser and navigate to **http://localhost:8050**

> The app downloads NLTK stopwords automatically on first run. The dataset must be present at `Dashboard/Source Data/Combined Data.csv`.

## Key Findings

- Normal is the largest category in the dataset, followed by Depression and Suicidal
- Posts related to Suicidal thoughts and Depression show higher negative polarity than Normal posts
- Negative sentiment posts significantly outnumber positive ones across all mental health categories
- Distinct keyword patterns emerge per category, confirming category-specific linguistic profiles

## Mental Health Resources

- [Befrienders Worldwide](https://www.befrienders.org/)
- [World Federation for Mental Health](https://wfmh.global/)
- [International Association for Suicide Prevention](https://www.iasp.info/)

## Team

- Aditya Jain
- Ryan Alex
- Rohit Kumar Malik
- Izaan Shumaiz
- Mohamed Sinan
