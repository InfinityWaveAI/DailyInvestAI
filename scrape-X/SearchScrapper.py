"""
Module for scraping tweets using Selenium WebDriver.

Classes:
- Tweet: Represents a single tweet with various attributes.
- SearchScrapper: Handles scraping of Twitter search queries.

"""

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from time import sleep
import random
import re

class Tweet:
    """
    Represents a tweet scraped from Twitter.

    Attributes:
    - ID: Unique identifier for the tweet.
    - author: Username of the tweet's author.    # only showing with id,date and text(content) but you can add more info #
    - fullName: Full name of the tweet's author.
    - content: Text content of the tweet.
    - timestamp: Timestamp of the tweet.
    - retweets: Number of retweets.
    - likes: Number of likes.
    - hashtag: Hashtag associated with the tweet.
    - views: Number of views.
    - comments: Number of comments.
    - bookmarks: Number of bookmarks.
    - image_url: URL of the attached image.
    - video_url: URL of the attached video (if any).
    - video_preview_image_url: URL of the video preview image.
    - hashtags: List of hashtags used in the tweet.
    - url: URL of the tweet.
    """
    def __init__(self, ID, author, fullName, content, timestamp, retweets, likes, hashtag, views, comments, bookmarks, image_url, video_url=None, video_preview_image_url=None, hashtags=None, url=None):
        self.ID = ID
        self.author = author
        self.fullName = fullName
        self.content = content
        self.timestamp = timestamp
        self.retweets = retweets
        self.likes = likes
        self.hashtag = hashtag
        self.views = views
        self.comments = comments
        self.bookmarks = bookmarks
        self.image_url = image_url
        self.video_url = video_url
        self.video_preview_image_url = video_preview_image_url
        self.hashtags = hashtags
        self.url = url

class SearchScrapper:
    """
    Scraper for Twitter (X) search queries.

    Methods:
    - scrape_twitter_query(query_url, hashtag, max_tweets): Scrapes tweets based on a search query URL.
    """
    def __init__(self, driver: webdriver.Chrome):
        """
        Initializes the SearchScrapper with a Selenium WebDriver instance.

        Parameters:
        - driver (webdriver.Chrome): The Selenium WebDriver instance.
        """
        self.driver = driver

    def scrape_twitter_query(self, query_url: str, hashtag: str, max_tweets: int):
        """
        Scrapes tweets from a given Twitter search query.

        Parameters:
        - query_url (str): URL for the Twitter search query.
        - hashtag (str): Associated hashtag for the search query.
        - max_tweets (int): Maximum number of tweets to scrape.

        Returns:
        - set[Tweet]: A set of Tweet objects containing scraped data.
        """
        self.driver.get(query_url)

        # Check for "No results" message
        no_results = False
        retries = 3
        for _ in range(retries):
            try:
                no_results_element = self.driver.find_element(By.CSS_SELECTOR, "span.css-1jxf684")
                if "No results" in no_results_element.text:
                    print(f"No results found for hashtag: {hashtag}")
                    no_results = True
                    break
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(0.5)

        if no_results:
            return set()

        # Wait for tweets to load
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
            )
        except TimeoutException:
            print(f"Timeout: No tweets found for hashtag: {hashtag}.")
            return set()

        print("Scraping...")
        hashtag_tweets = set()  # To store unique tweets
        processed_ids = set()  # To track processed tweet IDs
        prev_height = self.driver.execute_script('return document.body.scrollHeight')
        i = 0

        while len(hashtag_tweets) < max_tweets:
            try:
                loaded_tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
                for tweet in loaded_tweets:
                    if len(hashtag_tweets) >= max_tweets:
                        break

                    # Extract unique tweet ID from the URL
                    try:
                        tweet_link_element = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                        url = tweet_link_element.get_attribute('href')
                        tweet_id = url.split('/')[-1] if url else None
                    except NoSuchElementException:
                        tweet_id = None

                    if tweet_id and tweet_id in processed_ids:
                        continue  # Skip already processed tweets

                    # Extract data from each tweet

                    author = tweet.find_element(By.XPATH, './/span[contains(text(), "@")]').text.replace("@", "")
                    
                    try:
                        content = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                    except NoSuchElementException:
                        content = None

                    try:
                        full_name = tweet.find_element(By.XPATH, './/div[@data-testid="User-Name"]//span').text
                    except NoSuchElementException:
                        full_name = None

                    # Finding the post URL
                    try:
                        tweet_link_element = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                    except NoSuchElementException:
                        tweet_link_element = None

                    try:
                        url = tweet_link_element.get_attribute('href') if tweet_link_element else None
                    except NoSuchElementException:
                        url = None

                    # Extract the tweet ID from the URL
                    try:
                        tweet_id = url.split('/')[-1] if url else None
                    except NoSuchElementException:
                        tweet_id = None

                    
                    # Timestamp extraction
                    try:
                        timestamp_element = tweet.find_element(By.XPATH, './/time')
                        timestamp = timestamp_element.get_attribute('datetime')
                    except:
                        timestamp = "No timestamp available"

                    # Retweets, likes and comments extraction
                    retweet_count = tweet.find_element(By.XPATH, './/button[@data-testid="retweet"]').text
                    like_count = tweet.find_element(By.XPATH, './/button[@data-testid="like"]').text
                    comments = tweet.find_element(By.XPATH, './/button[@data-testid="reply"]').text
                    bookmarks = tweet.find_element(By.XPATH, './/button[@data-testid="bookmark"]').text

                    try:
                        views = tweet.find_element(By.XPATH, "//*[@role='group']").text.split('\n')[-1]
                    except NoSuchElementException:
                        views = None 

                    # Check for image URL
                    try:
                        tweet_photo_div = tweet.find_element(By.XPATH, './/div[@data-testid="tweetPhoto"]//img')
                        image_url = tweet_photo_div.get_attribute('src')  # Extract the image URL from the src attribute
                    except NoSuchElementException:
                        image_url = None 

                    # Check for video URL
                    try:
                        video_elements = tweet.find_elements(By.XPATH, './/div[@data-testid="videoPlayer"]//video')
                        video_url = video_elements[0].get_attribute('src') if video_elements else None
                        video_preview_image_url = video_elements[0].get_attribute('poster') if video_elements else None
                    except NoSuchElementException:
                        video_url = None
                        video_preview_image_url = None

                    hashtags = re.findall(r'#\w+', content)

                    # Add tweet to results
                    new_tweet = Tweet(
                        ID=tweet_id, author=author, fullName=full_name, content=content, timestamp=timestamp,
                        retweets=retweet_count, likes=like_count, hashtag=hashtag, views=views,
                        comments=comments, bookmarks=bookmarks, image_url=image_url, video_url=video_url,
                        video_preview_image_url=video_preview_image_url, hashtags=hashtags, url=url
                    )
                    hashtag_tweets.add(new_tweet)
                    processed_ids.add(tweet_id)  # Mark tweet as processed

                # Scroll to load more tweets
                self.driver.execute_script('window.scrollBy(0, 1000)')
                sleep(random.uniform(1, 3))
                curr_height = self.driver.execute_script('return document.body.scrollHeight')

                if curr_height == prev_height:
                    i += 1
                    if i == 10:
                        break
                else:
                    i = 0
                prev_height = curr_height

            except StaleElementReferenceException:
                pass

        print('Scraping complete.')
        return hashtag_tweets

