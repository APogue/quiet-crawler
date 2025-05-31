from dotenv import load_dotenv
import os
import praw
from prawcore import NotFound, Forbidden, ServerError, RequestException
import json
import logging

load_dotenv()

# check if .env is incomplete
required_env_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]
missing = [k for k in required_env_vars if not os.getenv(k)]
if missing:
    raise SystemExit(f"Missing required environment variables: {missing}")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
reddit_metadata = os.path.join(project_root, 'scraper_inputs', 'reddit', 'INC-001-reddit-urls.json')
json_scraper_dir = os.path.join(project_root, 'scraper_outputs', 'json')


# Setup, for more detail (e.g. inspect internal values), change level=logging.DEBUG
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

def load_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def reddit_scrape(input_file, output_dir):
    reddit_data = load_json_file(input_file)
    results = []

    for url in reddit_data.get("urls", []):
        try:
            submission = reddit.submission(url=url)
            # Force a fetch of the post if it’s not in cache
            submission.comments.replace_more(limit=0)
            submission_data = {
                "url": url,
                "title": submission.title,
                "author": str(submission.author),
                "score": submission.score,
                "created_utc": submission.created_utc,
                "num_comments": submission.num_comments,
                "selftext": submission.selftext,
            }
            results.append(submission_data)
            logging.info(f"Scraped: {url}")

        except NotFound:
            print(f"Submission not found (404): {url}")
        except Forbidden:
            print(f"Forbidden or removed (403): {url}")
      #  except RateLimitExceeded as rl:
         #   print(f"Rate limit hit for {url}: {rl}. You may need to wait and retry later.")
        except ServerError as se:
            print(f"Reddit server error for {url}: {se}. Try again in a moment.")
        except RequestException as re:
            # This will catch other network‐related issues in PRAW
            print(f"Network/API error for {url}: {re}")
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{reddit_data["incident_id"]}_reddit_scraped.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    logging.info(f"Saved Reddit data to {output_path}")

if __name__ == "__main__":
    reddit_scrape(reddit_metadata, json_scraper_dir)
