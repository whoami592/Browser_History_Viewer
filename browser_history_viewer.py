import sqlite3
import os
import platform
from datetime import datetime
import shutil
import getpass

def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════╗
    ║                                                    ║
    ║      BrowserHistoryViewer v1.0                     ║
    ║      Coded by Pakistani Ethical Hacker             ║
    ║      Mr. Sabaz Ali Khan                           ║
    ║                                                    ║
    ╚════════════════════════════════════════════════════╝
    """
    print(banner)

def convert_chrome_timestamp(chrome_time):
    """Convert Chrome's timestamp (microseconds since 1601-01-01) to readable format."""
    try:
        epoch_start = datetime(1601, 1, 1)
        delta = timedelta(microseconds=chrome_time)
        return epoch_start + delta
    except:
        return "Invalid timestamp"

def get_chrome_history():
    """Retrieve Chrome browser history."""
    history_db = ""
    if platform.system() == "Windows":
        history_db = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "History")
    elif platform.system() == "Darwin":  # macOS
        history_db = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Google", "Chrome", "Default", "History")
    else:  # Linux
        history_db = os.path.join(os.path.expanduser("~"), ".config", "google-chrome", "Default", "History")

    if not os.path.exists(history_db):
        print("[!] Chrome history database not found.")
        return []

    # Copy the database to avoid locked file issues
    temp_db = "temp_chrome_history"
    shutil.copyfile(history_db, temp_db)

    history = []
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
        for row in cursor.fetchall():
            url, title, visit_count, last_visit_time = row
            visit_time = convert_chrome_timestamp(last_visit_time)
            history.append((url, title, visit_count, visit_time))
        conn.close()
    except Exception as e:
        print(f"[!] Error accessing Chrome history: {e}")
    finally:
        os.remove(temp_db)  # Clean up temporary file
    return history

def get_firefox_history():
    """Retrieve Firefox browser history."""
    history_db = ""
    if platform.system() == "Windows":
        history_db = os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
    elif platform.system() == "Darwin":  # macOS
        history_db = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Firefox", "Profiles")
    else:  # Linux
        history_db = os.path.join(os.path.expanduser("~"), ".mozilla", "firefox")

    profile_path = ""
    if os.path.exists(history_db):
        profiles = [f for f in os.listdir(history_db) if f.endswith(".default-release")]
        if profiles:
            profile_path = os.path.join(history_db, profiles[0], "places.sqlite")

    if not os.path.exists(profile_path):
        print("[!] Firefox history database not found.")
        return []

    # Copy the database to avoid locked file issues
    temp_db = "temp_firefox_history"
    shutil.copyfile(profile_path, temp_db)

    history = []
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places")
        for row in cursor.fetchall():
            url, title, visit_count, last_visit_time = row
            visit_time = datetime.fromtimestamp(last_visit_time / 1000000) if last_visit_time else "Unknown"
            history.append((url, title, visit_count, visit_time))
        conn.close()
    except Exception as e:
        print(f"[!] Error accessing Firefox history: {e}")
    finally:
        os.remove(temp_db)  # Clean up temporary file
    return history

def display_history(history, browser_name):
    """Display the browser history in a formatted manner."""
    print(f"\n=== {browser_name} History ===")
    if not history:
        print(f"No history found for {browser_name}.")
        return
    print(f"{'URL':<80} {'Title':<50} {'Visits':<10} {'Last Visited':<25}")
    print("=" * 165)
    for url, title, visit_count, last_visit in history:
        title = title or "No Title"
        print(f"{url[:79]:<80} {title[:49]:<50} {visit_count:<10} {str(last_visit)[:24]:<25}")

def main():
    print_banner()
    print("[*] Fetching browser history...\n")

    # Get Chrome history
    chrome_history = get_chrome_history()
    display_history(chrome_history, "Google Chrome")

    # Get Firefox history
    firefox_history = get_firefox_history()
    display_history(firefox_history, "Mozilla Firefox")

if __name__ == "__main__":
    main()