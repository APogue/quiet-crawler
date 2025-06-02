import json
import os

# Paths
project_root = os.path.dirname(os.path.abspath(__file__)).split('utils')[0]
input_json = os.path.join(project_root, 'scraper_outputs', 'json', 'INC-001_reddit_scraped.json')
output_txt = os.path.join(project_root, 'scraper_outputs', 'raw_text', 'INC-001_reddit_scraped.txt')

# Ensure output directory exists
os.makedirs(os.path.dirname(output_txt), exist_ok=True)

# Load JSON
with open(input_json, 'r') as f:
    reddit_data = json.load(f)

# Write flattened text
with open(output_txt, 'w', encoding='utf-8') as f_out:
    for post in reddit_data:
        # Write post header
        f_out.write(f"URL: {post['url']}\n")
        f_out.write(f"Title: {post['title']}\n")
        f_out.write(f"Author: {post['author']}\n")
        f_out.write(f"Score: {post['score']}\n")
        f_out.write(f"Number of Comments: {post['num_comments']}\n")
        f_out.write("Post Text:\n")
        f_out.write(post['selftext'].strip() + "\n")
        f_out.write("="*80 + "\n")

        # Write top-level comments
        for top_comment in post.get('comments', []):
            f_out.write(f"[1] {top_comment['author']} (Score: {top_comment['score']}):\n")
            f_out.write(top_comment['body'].strip() + "\n")

            # Level 2 replies
            for level_2_comment in top_comment.get('replies', []):
                f_out.write(f"    [2] {level_2_comment['author']} (Score: {level_2_comment['score']}):\n")
                f_out.write("    " + level_2_comment['body'].strip() + "\n")

                # Level 3 replies
                for level_3_comment in level_2_comment.get('replies', []):
                    f_out.write(f"        [3] {level_3_comment['author']} (Score: {level_3_comment['score']}):\n")
                    f_out.write("        " + level_3_comment['body'].strip() + "\n")

            f_out.write("-"*80 + "\n")

        f_out.write("\n\n")
