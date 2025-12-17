import requests
import smtplib
import os
import time
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. SETUP CREDENTIALS
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASSWORD"]

# 2. CONFIGURATION
# We use a multi-reddit URL to scan all subs at once
TARGET_URL = "https://www.reddit.com/r/Entrepreneur+freelance+marketing+solopreneur/new.json?limit=50"
KEYWORDS = ["tax", "irs", "penalty", "safe harbor", "burnout", "overwhelmed", "drowning", "contract", "legal", "client"]
HEAT_THRESHOLD = 5  # Minimum comments
TIME_LIMIT_HOURS = 24

def send_email(posts):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER
    msg["Subject"] = f"🧛 Vampire Scout: {len(posts)} Hot Leads Found"

    body = "<h3>The Scout found these conversations for you:</h3><ul>"
    for post in posts:
        body += f"<li><b>[{post['sub']}]</b> <a href='{post['url']}'>{post['title']}</a><br>Comments: {post['comments']} | Heat: 🔥</li><br>"
    body += "</ul>"
    
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        server.quit()
        print(f"✅ Email sent with {len(posts)} leads.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def run_scout():
    print("🕵️ Scout is waking up...")
    
    # Custom User-Agent is REQUIRED to avoid being blocked
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; VampireScout/1.0; +http://creatoraiplaybook.co)'}
    
    try:
        response = requests.get(TARGET_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error fetching Reddit data: {response.status_code}")
            return
            
        data = response.json()
        posts = data['data']['children']
        hot_leads = []

        for p in posts:
            post = p['data']
            
            # 1. Keyword Check
            title_text = post['title'].lower()
            self_text = post.get('selftext', '').lower()
            if not any(k in title_text or k in self_text for k in KEYWORDS):
                continue

            # 2. Heat Check
            if post['num_comments'] < HEAT_THRESHOLD:
                continue

            # 3. Time Check
            created_time = datetime.datetime.fromtimestamp(post['created_utc'])
            age = datetime.datetime.now() - created_time
            if age.total_seconds() > (TIME_LIMIT_HOURS * 3600):
                continue

            print(f"🔥 Found lead: {post['title']}")
            hot_leads.append({
                "title": post['title'],
                "url": f"https://www.reddit.com{post['permalink']}",
                "sub": post['subreddit'],
                "comments": post['num_comments']
            })

        if hot_leads:
            send_email(hot_leads)
        else:
            print("❄️ No leads found this cycle.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    run_scout()
