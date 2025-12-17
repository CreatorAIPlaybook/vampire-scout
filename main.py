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
TARGET_URL = "https://www.reddit.com/r/Entrepreneur+freelance+marketing+solopreneur/new.json?limit=50"
KEYWORDS = ["tax", "irs", "penalty", "safe harbor", "burnout", "overwhelmed", "drowning", "contract", "legal", "client"]
HEAT_THRESHOLD = 5 
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
    
    # THE FIX: Mimic a real Chrome Browser on a Mac
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        # We try fetching OLD reddit JSON first, it's often less protected
        response = requests.get(TARGET_URL, headers=headers)
        
        if response.status_code == 403:
            print("❌ Reddit blocked the request (403). They detected the server IP.")
            return
        elif response.status_code != 200:
            print(f"❌ Error fetching Reddit data: {response.status_code}")
            return
            
        data = response.json()
        posts = data['data']['children']
        hot_leads = []

        for p in posts:
            post = p['data']
            
            title_text = post['title'].lower()
            self_text = post.get('selftext', '').lower()
            if not any(k in title_text or k in self_text for k in KEYWORDS):
                continue

            if post['num_comments'] < HEAT_THRESHOLD:
                continue

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
