import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
from datetime import datetime
import logging
import time
import random
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.setup_driver()
        
    def setup_driver(self):
        """Set up the Chrome driver with options"""
        try:
            # Set up Chrome options
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Add random user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Initialize the undetected Chrome driver
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up driver: {str(e)}")
            raise
        
    def random_sleep(self, min_seconds=2, max_seconds=5):
        """Sleep for a random amount of time to appear more human-like"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def simulate_human_behavior(self):
        """Simulate human-like behavior"""
        try:
            # Scroll randomly
            for _ in range(random.randint(1, 3)):
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
                self.random_sleep(1, 2)
                
            # Move mouse randomly (simulated)
            self.driver.execute_script("""
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': arguments[0],
                    'clientY': arguments[1]
                });
                document.dispatchEvent(event);
            """, random.randint(0, 1000), random.randint(0, 1000))
        except Exception as e:
            logger.warning(f"Error in human behavior simulation: {str(e)}")
    
    def login(self):
        """Login to Twitter"""
        try:
            logger.info("Attempting to login to Twitter...")
            
            # Go to Twitter login page
            self.driver.get("https://twitter.com/i/flow/login")
            self.random_sleep(3, 5)
            
            # Wait for username field and enter username
            username_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
            username_field.send_keys(self.username)
            self.random_sleep(1, 2)
            
            # Click next button
            next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
            next_button.click()
            self.random_sleep(2, 3)
            
            # Check for verification after username
            try:
                verification_text = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'unusual login activity')]")))
                logger.info("Verification required, entering phone number...")
                
                # Enter phone number with country code
                phone_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
                phone_field.send_keys("")  # Adding +1 for US country code
                self.random_sleep(1, 2)
                
                # Click next button
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
                next_button.click()
                
                # Wait for verification to complete
                self.random_sleep(5, 7)
                
            except Exception as e:
                logger.info("No verification required or verification failed")
            
            # Wait for password field and enter password
            password_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
            password_field.send_keys(self.password)
            self.random_sleep(1, 2)
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']")))
            login_button.click()
            
            # Wait for login to complete
            self.random_sleep(5, 7)
            
            # Check if login was successful
            if "home" in self.driver.current_url:
                logger.info("Successfully logged in to Twitter")
                return True
            else:
                logger.error("Login failed - not redirected to home page")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def save_tweets_to_csv(self, tweets, filename):
        """Save tweets to CSV file"""
        try:
            if not tweets:  # Don't try to save if no tweets
                return
                
            # Convert to DataFrame with explicit columns
            new_tweets_df = pd.DataFrame(tweets, columns=[
                'username', 'content', 'date', 'likes', 'retweets', 'replies', 'timestamp'
            ])
            
            # If file exists, append to it
            if os.path.exists(filename):
                try:
                    existing_df = pd.read_csv(filename)
                    combined_df = pd.concat([existing_df, new_tweets_df], ignore_index=True)
                except Exception as e:
                    logger.warning(f"Error reading existing CSV, creating new file: {str(e)}")
                    combined_df = new_tweets_df
            else:
                combined_df = new_tweets_df
            
            # Remove duplicates based on content and username
            combined_df = combined_df.drop_duplicates(subset=['content', 'username'])
            
            # Save to CSV
            combined_df.to_csv(filename, index=False)
            logger.info(f"Successfully saved {len(new_tweets_df)} tweets to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving tweets to CSV: {str(e)}")
            # Print the tweets for debugging
            logger.error(f"Tweets that failed to save: {tweets}")

    def scroll_and_extract_tweets(self, max_tweets=20):
        """Scroll through the page and extract tweets"""
        tweets = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 30  # Increased for more tweets
        
        while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
            try:
                # Wait for tweets to load
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]')))
                
                # Get all tweet elements
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                for tweet in tweet_elements:
                    if len(tweets) >= max_tweets:
                        break
                        
                    try:
                        # Extract tweet data using Selenium
                        tweet_data = {
                            'username': None,
                            'content': None,
                            'date': None,
                            'likes': None,
                            'retweets': None,
                            'replies': None,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Get username
                        try:
                            username_element = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                            tweet_data['username'] = username_element.text.split('\n')[0]
                        except:
                            pass
                        
                        # Get tweet content
                        try:
                            content_element = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                            tweet_data['content'] = content_element.text
                        except:
                            pass
                        
                        # Get date
                        try:
                            date_element = tweet.find_element(By.TAG_NAME, 'time')
                            tweet_data['date'] = date_element.get_attribute('datetime')
                        except:
                            pass
                        
                        # Get engagement metrics
                        try:
                            metrics = tweet.find_elements(By.CSS_SELECTOR, 'div[data-testid$="-count"]')
                            for metric in metrics:
                                metric_type = metric.get_attribute('data-testid')
                                if 'like' in metric_type:
                                    tweet_data['likes'] = metric.text
                                elif 'retweet' in metric_type:
                                    tweet_data['retweets'] = metric.text
                                elif 'reply' in metric_type:
                                    tweet_data['replies'] = metric.text
                        except:
                            pass
                        
                        # Only add tweet if it has content
                        if tweet_data['content']:
                            tweets.append(tweet_data)
                            logger.info(f"Extracted tweet: {tweet_data['content'][:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"Error extracting tweet: {str(e)}")
                        continue
                
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_sleep(2, 3)
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = new_height
                
                # Simulate human behavior
                self.simulate_human_behavior()
                
            except Exception as e:
                logger.warning(f"Error during scrolling: {str(e)}")
                # Pause for a longer time
                logger.info("Pausing for 30 seconds before continuing...")
                time.sleep(30)
                
                # Simulate human behavior again
                self.simulate_human_behavior()
                
                # Try to relogin
                try:
                    if not self.login():
                        logger.error("Failed to relogin after error")
                        return tweets
                except Exception as login_error:
                    logger.error(f"Error during relogin: {str(login_error)}")
                    return tweets
                
                continue
        
        return tweets
    
    def get_user_tweets(self, username, max_tweets=20):
        """Get the first 20 posts from a user's profile"""
        try:
            logger.info(f"Fetching posts from @{username}'s profile")
            
            # Go to user's main profile
            self.driver.get(f"https://twitter.com/{username}")
            self.random_sleep(3, 5)
            
            # Scroll and extract tweets
            tweets = self.scroll_and_extract_tweets(max_tweets)
            
            if tweets:
                # Save tweets immediately after getting them from this user
                timestamp = datetime.now().strftime("%Y%m%d")
                filename = f"data/raw/tweets_{timestamp}.csv"
                self.save_tweets_to_csv(tweets, filename)
                logger.info(f"Successfully fetched and saved {len(tweets)} tweets from @{username}")
            else:
                logger.warning(f"No tweets collected from @{username}")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error fetching tweets for @{username}: {str(e)}")
            return []
    
    def get_trending_tweets(self, max_tweets_per_trend=5):
        """Go to trending page, click each trend by index, wait, scroll and scrape, wait, go back, repeat for all trends."""
        try:
            logger.info("Fetching tweets from trending topics (sequentially)")
            self.driver.get("https://x.com/explore/tabs/trending")
            self.random_sleep(5, 7)

            tweets = []
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="trend"]')))
            self.random_sleep(2, 3)
            num_trends = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="trend"]'))
            logger.info(f"Found {num_trends} trending topics")

            # Prepare filename for saving
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"data/raw/tweets_{timestamp}.csv"

            for i in range(num_trends):
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="trend"]')))
                    self.random_sleep(2, 3)
                    trending_topics = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="trend"]')
                    if i >= len(trending_topics):
                        logger.info(f"Trend index {i} out of range after reload, stopping.")
                        break
                    topic = trending_topics[i]
                    logger.info(f"Clicking on trending topic {i+1} (using ActionChains and JS click)")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", topic)
                    self.random_sleep(1, 2)
                    try:
                        ActionChains(self.driver).move_to_element(topic).pause(0.5).perform()
                        self.random_sleep(0.5, 1)
                        self.driver.execute_script("arguments[0].click();", topic)
                    except Exception as click_e:
                        logger.warning(f"ActionChains/JS click failed: {click_e}, trying normal click...")
                        try:
                            topic.click()
                        except Exception as fallback_e:
                            logger.error(f"Fallback click also failed: {fallback_e}")
                            continue
                    self.random_sleep(5, 8)

                    num_scrolls = random.randint(1, 3)
                    for _ in range(num_scrolls):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        self.random_sleep(2, 4)
                        self.simulate_human_behavior()

                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]')))
                    self.random_sleep(2, 3)
                    tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')[:max_tweets_per_trend]
                    logger.info(f"Found {len(tweet_elements)} tweets in current topic")

                    for tweet in tweet_elements:
                        try:
                            tweet_data = {
                                'username': None,
                                'content': None,
                                'date': None,
                                'likes': 0,
                                'retweets': 0,
                                'replies': 0,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            try:
                                username_element = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                                tweet_data['username'] = username_element.text.split('\n')[0]
                            except:
                                pass
                            try:
                                content_element = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                                tweet_data['content'] = content_element.text
                            except:
                                continue
                            try:
                                date_element = tweet.find_element(By.TAG_NAME, 'time')
                                tweet_data['date'] = date_element.get_attribute('datetime')
                            except:
                                pass
                            try:
                                metrics = tweet.find_elements(By.CSS_SELECTOR, 'div[data-testid$="-count"]')
                                for metric in metrics:
                                    metric_type = metric.get_attribute('data-testid')
                                    if 'like' in metric_type:
                                        tweet_data['likes'] = metric.text
                                    elif 'retweet' in metric_type:
                                        tweet_data['retweets'] = metric.text
                                    elif 'reply' in metric_type:
                                        tweet_data['replies'] = metric.text
                            except:
                                pass
                            if tweet_data['content']:
                                tweets.append(tweet_data)
                                logger.info(f"Extracted tweet: {tweet_data['content'][:50]}...")
                                # Save this tweet immediately
                                self.save_tweets_to_csv([tweet_data], filename)
                        except Exception as e:
                            logger.warning(f"Error extracting tweet: {str(e)}")
                            continue

                    self.random_sleep(5, 10)
                    logger.info("Returning to trending page...")
                    self.driver.get("https://x.com/explore/tabs/trending")
                    self.random_sleep(5, 8)
                except Exception as e:
                    logger.warning(f"Error processing trending topic {i+1}: {str(e)}")
                    self.driver.get("https://x.com/explore/tabs/trending")
                    self.random_sleep(5, 8)
                    continue

            if tweets:
                logger.info(f"Successfully fetched and saved {len(tweets)} tweets from trending topics")
            else:
                logger.warning("No tweets collected from trending topics")
            return tweets
        except Exception as e:
            logger.error(f"Error fetching trending tweets: {str(e)}")
            return []
    
    def close(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

def signal_handler(signum, frame):
    """Handle cleanup on program termination"""
    logger.info("Received termination signal. Cleaning up...")
    if scraper:
        scraper.close()
    sys.exit(0)

def main():
    global scraper
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create data directory if it doesn't exist
    os.makedirs("data/raw", exist_ok=True)
    
    while True:
        try:
            # Initialize scraper with your credentials
            scraper = TwitterScraper(
                username="",
                password=""
            )
            
            # Login to Twitter
            if not scraper.login():
                logger.error("Failed to login. Retrying in 60 seconds...")
                time.sleep(60)
                continue
            
            try:
                # Get tweets from trending topics
                tweets = scraper.get_trending_tweets(max_tweets_per_trend=5)
                
                if tweets:
                    logger.info(f"Successfully collected {len(tweets)} tweets from trending topics")
                else:
                    logger.warning("No tweets collected, will retry after relogin")
                
                # Add a delay before next cycle
                delay = random.uniform(10, 15)
                logger.info(f"Waiting {delay:.1f} seconds before next cycle...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing trending topics: {str(e)}")
                # If error occurs, try to relogin and retry
                logger.info("Attempting to relogin and retry...")
                if scraper.login():
                    logger.info("Successfully relogged in, will retry")
                else:
                    logger.error("Failed to relogin, waiting 60 seconds before retry...")
                    time.sleep(60)
                continue
            
            # Close the browser and wait before starting again
            scraper.close()
            logger.info("Completed one cycle. Waiting 300 seconds before starting next cycle...")
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            if scraper:
                scraper.close()
            logger.info("Waiting 60 seconds before retrying...")
            time.sleep(60)

if __name__ == "__main__":
    scraper = None
    main()
