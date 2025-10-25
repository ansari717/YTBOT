# main.py
import os, shutil, glob, sys, traceback
from redvid import Downloader
import config
import reddit_scraper
import upload
import render
from store import get_store

def pick_candidate(candidates, store, max_duration):
    for vid in candidates:
        url = vid["url"]
        if store.seen(url):
            continue

        dur = vid.get("duration")
        if dur is None:
            # As a fallback, probe via redvid
            try:
                d = Downloader(max_q=True)
                d.url = url
                dur = getattr(d, "duration", None)
            except Exception:
                dur = None

        if dur is None:
            print(f"Skipping (unknown duration): {url}")
            continue

        if dur <= max_duration:
            return vid

    return None

def main():
    store = get_store()

    # Clean temp dir
    temp_dir = config.TEMP_DIR
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # Scrape
    vids = reddit_scraper.scrape_reddit(config.SUBREDDITS)
    cand = pick_candidate(vids, store, config.MAX_DURATION_SECONDS)
    if not cand:
        print(f"No eligible videos ≤{config.MAX_DURATION_SECONDS}s not already processed.")
        return False

    print("Chosen video:", cand)

    # Download
    reddit_scraper.download_vid(cand["url"], temp_dir)

    mp4s = sorted(glob.glob(os.path.join(temp_dir, "*.mp4")))
    if not mp4s:
        print("Download produced no .mp4 files.")
        return False

    src = mp4s[0]
    main_name = "main_clip.mp4"
    dst_main = os.path.join(temp_dir, main_name)
    if src != dst_main:
        shutil.copy(src, dst_main)

    # Render
    out_name = "output.mp4"
    render.render(temp_dir, main_name, out_name, config.VIDEO["dimensions"])
    out_path = os.path.join(temp_dir, out_name)

    # Prepare metadata
    title = f"{cand['title']} #shorts"
    description = f"Video by: {cand['author']}\nSource: {cand['url']}"
    meta = {
        "title": title,
        "description": description,
        "tags": config.YOUTUBE["tags"],
        "category": config.YOUTUBE["category"],
        "status": config.YOUTUBE["status"],
        "made_for_kids": config.YOUTUBE["made_for_kids"],
    }

    print("Uploading...")
    resp = upload.upload(out_path, meta)
    if resp:
        store.mark(cand["url"])
        print("Video uploaded successfully! Check YouTube.")
        return True

    print("Upload failed.")
    return False

if __name__ == "__main__":
    try:
        ok = main()
        sys.exit(0 if ok else 1)
    except Exception:
        print("Fatal error:\n", traceback.format_exc())
        sys.exit(2)
