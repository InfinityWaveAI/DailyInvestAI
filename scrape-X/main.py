"""
Main script to scrape data from Twitter (X) based on the user's requirements.

Features:
- Scrapes tweets based on hashtags (modee=0).
- Scrapes tweets from specific user timelines (mode=1).

"""

import time
import pandas as pd
from WebDriverSetup import setup_web_driver
from SearchScrapper import SearchScrapper
from datetime import datetime, timedelta

def main(mode):
    """
    Entry point for scraping tasks.

    Parameters:
    - mode (int): Determines the scraping mode.
        - 0: Scrape tweets using hashtags for specific dates.
        - 1: Scrape tweets from user timelines.
    """
    start_time = time.time()
    driver = setup_web_driver()


    if mode == 0:
        # Hashtag scraping
        hashtags = ["StockMarket", "BullMarket", "TechStocks", "CryptoMarket", "StockAlert", "MarketNews",]
        # Replace or extend this list with relevant hashtags.
        start_date = "2025-01-02"
        end_date = "2025-01-03"



        all_tweets = []

        for hashtag in hashtags:
            search_query = f'https://x.com/search?q=%28%23{hashtag}%29+until%3A{end_date}+since%3A{start_date}&src=typed_query&f=live'
            scraped_tweets = SearchScrapper(driver).scrape_twitter_query(search_query, hashtag, max_tweets=50)

            # Process and format tweet data
            tweets_data = [
                (
                    tweet.ID, tweet.timestamp, tweet.content,
                    # tweet.ID, tweet.author, tweet.fullName, tweet.url, 
                    # tweet.image_url, None, None, tweet.video_url, tweet.video_preview_image_url,
                    # None, None, None, None, tweet.comments, tweet.retweets, None, tweet.likes,
                    # tweet.hashtags, tweet.views, hashtag
                )
                for tweet in scraped_tweets
            ]
            all_tweets.extend(tweets_data)

        # Save results
        columns = [
            'id','Date&time', 'text',
            # 'username', 'fullname', 'url', 'publication_date', 'photo_url',
            # 'photo_preview_image_url', 'photo_alt_text', 'video_url', 'video_preview_image_url',
            # 'video_alt_text', 'animated_gif_url', 'animated_gif_preview_image_url', 'animated_gif_alt_text',
            # 'replies', 'retweets', 'quotes', 'likes', 'hashtags', 'views', 'target'
        ]
        df = pd.DataFrame(all_tweets, columns=columns)
        df.to_csv(f"{start_date}_to_{end_date}_hashtag_tweets.csv", index=False, encoding="utf-8-sig")
        print(f"Data saved to {start_date}_to_{end_date}_hashtag_tweets.csv")

    elif mode == 1:
        # User timeline scraping
        users = ['REDBOXINDIA']  # Replace 
        
        

        # start_date = "2025-01-05"
        # end_date = "2025-01-03"
        
        # Automatic latest yesterdays : TODO change accordingly
        c = datetime.today() 
        today = c.strftime("%Y") + "-" + c.strftime("%m") + "-" + c.strftime("%d") 

        c = datetime.today() - timedelta(1)
        yesterday = c.strftime("%Y") + "-" + c.strftime("%m") + "-" + c.strftime("%d") 
        
        # not one day past :> One week past 
        c = datetime.today() - timedelta(7)
        week_past = c.strftime("%Y") + "-" + c.strftime("%m") + "-" + c.strftime("%d") 

        start_date = week_past
        end_date = today

        all_tweets = []

        for user in users:
            search_query = f'https://x.com/search?q=%28from%3A{user}%29+since%3A{start_date}&src=typed_query&f=live'
            scraped_tweets = SearchScrapper(driver).scrape_twitter_query(search_query, user, max_tweets=50)

            tweets_data = [
                (
                    user, tweet.ID,  tweet.timestamp, tweet.content.strip()
                    # , tweet.author, tweet.fullName, tweet.url,
                    # tweet.image_url, None, None, tweet.video_url, tweet.video_preview_image_url,
                    # None, None, None, None, tweet.comments, tweet.retweets, None, tweet.likes,
                    # tweet.hashtags, tweet.views, user
                )
                for tweet in scraped_tweets
            ]
            all_tweets.extend(tweets_data)

        # Save results
        columns = [
            'user', 'id','Date&Time','text'
            # 'username', 'fullname', 'url', 'publication_date', 'photo_url',
            # 'photo_preview_image_url', 'photo_alt_text', 'video_url', 'video_preview_image_url',
            # 'video_alt_text', 'animated_gif_url', 'animated_gif_preview_image_url', 'animated_gif_alt_text',
            # 'replies', 'retweets', 'quotes', 'likes', 'hashtags', 'views', 'target'
        ]
        df = pd.DataFrame(all_tweets, columns=columns)
        df.to_csv(f"{start_date}_to_{end_date}_user_tweets.csv", index=False, encoding="utf-8-sig")
        print(f"Data saved to {start_date}_to_{end_date}_user_tweets.csv")

    else:
        print("Invalid side argument. Use 0 for hashtags or 1 for user timelines.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to run the script: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    # Replace with the appropriate side argument: 0, 1, or 3
    main(mode=1)