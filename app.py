from flask import Flask, render_template, request, jsonify
import pandas as pd
from textblob import TextBlob
import numpy as np
import plotly.express as px
import plotly.utils
import json
from datetime import datetime

app = Flask(__name__)

def analyze_tweet_sentiments(file):
    """
    Analyze sentiments from uploaded CSV file
    """
    # Read the CSV file
    df = pd.read_csv(file)
    
    # Function to get sentiment scores
    def get_sentiment(text):
        try:
            if pd.isna(text):
                return np.nan, np.nan
            analysis = TextBlob(str(text))
            return analysis.sentiment.polarity, analysis.sentiment.subjectivity
        except Exception as e:
            print(f"Error analyzing tweet: {e}")
            return np.nan, np.nan
    
    # Apply sentiment analysis
    df[['polarity', 'subjectivity']] = df['text'].apply(lambda x: pd.Series(get_sentiment(x)))
    
    # Add sentiment category
    def get_sentiment_category(polarity):
        if pd.isna(polarity):
            return 'neutral'
        elif polarity > 0:
            return 'positive'
        elif polarity < 0:
            return 'negative'
        else:
            return 'neutral'
    
    df['sentiment'] = df['polarity'].apply(get_sentiment_category)
    
    # Convert datetime
    df['Date&Time'] = pd.to_datetime(df['Date&Time'])
    df['date'] = df['Date&Time'].dt.date
    
    # Calculate daily sentiment counts
    daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
    
    # Create sentiment trend plot
    fig = px.line(daily_sentiment, 
                  title='Sentiment Trends Over Time',
                  labels={'value': 'Number of Tweets', 'date': 'Date'})
    
    sentiment_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Calculate summary statistics
    sentiment_stats = {
        'total_tweets': len(df),
        'positive_tweets': len(df[df['sentiment'] == 'positive']),
        'negative_tweets': len(df[df['sentiment'] == 'negative']),
        'neutral_tweets': len(df[df['sentiment'] == 'neutral']),
        'average_polarity': round(df['polarity'].mean(), 3),
        'average_subjectivity': round(df['subjectivity'].mean(), 3)
    }
    
    # Convert DataFrame to dictionary for display
    tweets_data = df[['Date&Time', 'text', 'sentiment', 'polarity']].to_dict('records')
    
    return sentiment_stats, tweets_data, sentiment_plot

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400
        
        try:
            sentiment_stats, tweets_data, sentiment_plot = analyze_tweet_sentiments(file)
            return render_template('results.html', 
                                stats=sentiment_stats, 
                                tweets=tweets_data,
                                sentiment_plot=sentiment_plot)
        except Exception as e:
            return f'Error processing file: {str(e)}', 400
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)