# reddit_scraper.py
import praw
from redvid import Downloader
import config

def _reddit_client():
    rl = config.REDDIT_LOGIN
    if rl.get("client_id") and rl.get("client_secret") and rl.get("user_agent"):
        if rl.get("username") and rl.get("password"):
            return praw.Reddit(
                client_id=rl["client_id"],
                client_secret=rl["client_secret"],
                user_agent=rl["user_agent"],
                username=rl["username"],
                password=rl["password"],
            )
        # Read-only
        r = praw.Reddit(
            client_id=rl["client_id"],
            client_secret=rl["client_secret"],
            user_agent=rl["user_agent"],
        )
        r.read_only = True
        return r
    raise RuntimeError("Missing Reddit credentials: set REDDIT_CLIENT_ID/SECRET/USER_AGENT")

def download_vid(url, directory):
    print(f"Attempting to download reddit video: {url}")
    dl = Downloader(max_q=True)
    dl.url = url
    dl.path = directory
    dl.download()

def scrape_reddit(subreddits):
    """
    Returns: list of dicts {url, title, author, duration}
    """
    print("Logging into Reddit...")
    red = _reddit_client()
    print("Login success. Fetching posts...")
    subs = red.subreddit(subreddits).hot(limit=100)
    out = []
    for s in subs:
        if s.stickied or s.over_18:
            continue
        url = s.url or ""
        domain = getattr(s, "domain", "")
        if "v.redd.it" not in url and domain != "v.redd.it":
            continue

        author = s.author.name if s.author else "[deleted]"

        # Try to read duration from media info (seconds)
        dur = None
        m = s.media or s.secure_media
        if isinstance(m, dict) and "reddit_video" in m:
            rv = m.get("reddit_video") or {}
            dur = rv.get("duration")

        out.append({
            "url": url,
            "title": s.title,
            "author": author,
            "duration": dur,
        })
    print(f"Found {len(out)} candidate videos.")
    return out
