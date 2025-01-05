# Twitter Scraper

A Python-based scraper for extracting data from Twitter (X) using Selenium WebDriver. The scraper supports two main functionalities: scraping tweets based on hashtags and user timelines.

## Features

- **Hashtag Scraping (`mode=0`)**
  - Scrape tweets associated with specific hashtags within a date range.
- **User Timeline Scraping (`mode=1`)**
  - Scrape tweets from the timelines of specific users within a date range.

## Prerequisites

1. **Python 3.8+**

   - Ensure Python is installed on your system.

2. **Google Chrome**
   - Ensure Google Chrome is installed on your system.

## Installation

## File Overview and Explanation

### `main.py`

- **Purpose**: Serves as the entry point for the scraper, handling different modes (`side` values) for scraping.
- **Key Functions**:
  - `side=0`: Scrapes tweets using hashtags for a given date range.
  - `side=1`: Scrapes tweets from the timelines of specified users.
  - `side=3`: Scrapes followers, following, and verified followers of specified users.
- **Output**: Saves the scraped data as CSV files.

### `SearchScrapper.py`

- **Purpose**: Handles the logic for scraping tweets based on hashtags or user timelines.
- **Key Features**:
  - Uses Selenium WebDriver to navigate Twitter search queries.
  - Extracts tweet data, including text, author, likes, retweets, hashtags, and more.
  - Implements a deduplication mechanism to avoid processing the same tweet multiple times.
- **Output**: Returns a set of unique `Tweet` objects containing all relevant data.

### `WebDriverSetup.py`

- **Purpose**: Configures and initializes the Selenium WebDriver.
- **Key Features**:
  - Uses `webdriver-manager` to automatically download and manage the ChromeDriver.
  - Handles Twitter login with placeholder credentials.
  - Prepares the WebDriver for scraping tasks.
- **Output**: Returns a ready-to-use Selenium WebDriver instance.

## Usage

1. **Run the Program**

   - Open a terminal in the project directory and run:
     ```bash
     python main.py
     ```

2. **Choose a Scraping Mode**

   - Set the `mode` parameter in `main.py`:
     - `mode=0`: Scrape tweets using hashtags.
     - `mode=1`: Scrape tweets from user timelines.

3. **View Results**
   - Results are saved as CSV files in the project directory:
     - Hashtag tweets: `<start_date>_to_<end_date>_hash_tweets.csv`
     - User tweets: `<start_date>_to_<end_date>_user_tweets.csv`

## Example

### Scraping Tweets Using Hashtags

1. Set `mode=0` in `main.py`.
2. Specify hashtags, start date, and end date.
3. Run the program to generate a CSV of tweets for the specified hashtags.

### Scraping User Timelines

1. Set `mode=1` in `main.py`.
2. Specify usernames, start date, and end date.
3. Run the program to generate a CSV of tweets from the specified user timelines.

mail - dandriyalajay4@gmail.com
