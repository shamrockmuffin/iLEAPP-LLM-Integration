import os
import json
import pandas as pd
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta

# Sample data generator for testing the LLM-enhanced forensic analysis capabilities
class SampleDataGenerator:
    """
    Generates sample iOS forensic data for testing the LLM-enhanced analysis capabilities.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the sample data generator.
        
        Args:
            output_dir: Directory to save sample data
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdirectories for different artifact types
        self.sms_dir = os.path.join(output_dir, "sms")
        self.app_usage_dir = os.path.join(output_dir, "app_usage")
        self.itunes_dir = os.path.join(output_dir, "itunes_music")
        self.chrome_dir = os.path.join(output_dir, "chrome_history")
        
        os.makedirs(self.sms_dir, exist_ok=True)
        os.makedirs(self.app_usage_dir, exist_ok=True)
        os.makedirs(self.itunes_dir, exist_ok=True)
        os.makedirs(self.chrome_dir, exist_ok=True)
    
    def generate_all_sample_data(self):
        """
        Generate sample data for all artifact types.
        """
        self.generate_sms_data()
        self.generate_app_usage_data()
        self.generate_itunes_music_data()
        self.generate_chrome_history_data()
        
        print(f"All sample data generated in {self.output_dir}")
    
    def generate_sms_data(self):
        """
        Generate sample SMS data.
        """
        db_path = os.path.join(self.sms_dir, "sms.db")
        
        # Create SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS message (
            rowid INTEGER PRIMARY KEY,
            date INTEGER,
            text TEXT,
            is_from_me INTEGER,
            handle_id INTEGER
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS handle (
            rowid INTEGER PRIMARY KEY,
            id TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            rowid INTEGER PRIMARY KEY,
            chat_identifier TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_message_join (
            chat_id INTEGER,
            message_id INTEGER,
            PRIMARY KEY (chat_id, message_id)
        )
        ''')
        
        # Insert sample contacts
        contacts = [
            (1, "+1234567890"),  # John
            (2, "+1987654321"),  # Sarah
            (3, "+1555123456"),  # Work
            (4, "email@example.com")  # Email
        ]
        
        cursor.executemany("INSERT INTO handle (rowid, id) VALUES (?, ?)", contacts)
        
        # Insert sample chats
        chats = [
            (1, "+1234567890"),  # John
            (2, "+1987654321"),  # Sarah
            (3, "+1555123456"),  # Work
            (4, "email@example.com")  # Email
        ]
        
        cursor.executemany("INSERT INTO chat (rowid, chat_identifier) VALUES (?, ?)", chats)
        
        # Generate sample messages
        now = datetime.now()
        messages = []
        chat_messages = []
        
        # Conversation with John
        john_convo = [
            (now - timedelta(days=5, hours=3), "Hey, how's it going?", 0, 1),
            (now - timedelta(days=5, hours=3, minutes=2), "Good! Just finished that project we talked about.", 1, 1),
            (now - timedelta(days=5, hours=3, minutes=5), "Nice! Can you send me the files?", 0, 1),
            (now - timedelta(days=5, hours=3, minutes=10), "Sure, I'll email them to you tonight.", 1, 1),
            (now - timedelta(days=3, hours=1), "Did you get a chance to send those files?", 0, 1),
            (now - timedelta(days=3, hours=1, minutes=30), "Sorry for the delay. Just sent them!", 1, 1),
            (now - timedelta(days=3, hours=1, minutes=35), "Got them, thanks!", 0, 1),
            (now - timedelta(days=1, hours=2), "Are we still meeting tomorrow at 2pm?", 0, 1),
            (now - timedelta(days=1, hours=2, minutes=5), "Yes, at the usual coffee shop.", 1, 1),
            (now - timedelta(days=1, hours=2, minutes=10), "Perfect, see you then!", 0, 1)
        ]
        
        # Conversation with Sarah
        sarah_convo = [
            (now - timedelta(days=7, hours=5), "Hey Sarah, are you coming to the party this weekend?", 1, 2),
            (now - timedelta(days=7, hours=5, minutes=20), "I'm not sure yet. What time is it?", 0, 2),
            (now - timedelta(days=7, hours=5, minutes=25), "It starts at 8pm on Saturday.", 1, 2),
            (now - timedelta(days=7, hours=5, minutes=40), "I might be able to make it. I'll let you know by Friday.", 0, 2),
            (now - timedelta(days=2, hours=4), "Have you decided about the party?", 1, 2),
            (now - timedelta(days=2, hours=4, minutes=10), "Yes, I'll be there! Should I bring anything?", 0, 2),
            (now - timedelta(days=2, hours=4, minutes=15), "Just yourself! Looking forward to seeing you.", 1, 2),
            (now - timedelta(days=2, hours=4, minutes=20), "Great! See you tomorrow then.", 0, 2)
        ]
        
        # Work conversation
        work_convo = [
            (now - timedelta(days=10, hours=9), "Meeting has been moved to 3pm today.", 0, 3),
            (now - timedelta(days=10, hours=9, minutes=5), "Thanks for letting me know. I'll be there.", 1, 3),
            (now - timedelta(days=8, hours=14), "Can you send me the Q1 report?", 0, 3),
            (now - timedelta(days=8, hours=14, minutes=30), "Just sent it to your email.", 1, 3),
            (now - timedelta(days=8, hours=14, minutes=45), "Got it, thanks!", 0, 3),
            (now - timedelta(days=4, hours=10), "Are you available for a call at 2pm?", 0, 3),
            (now - timedelta(days=4, hours=10, minutes=15), "Yes, I'll be free then.", 1, 3),
            (now - timedelta(days=1, hours=16), "Don't forget about the team lunch tomorrow.", 0, 3),
            (now - timedelta(days=1, hours=16, minutes=5), "I won't! Looking forward to it.", 1, 3)
        ]
        
        # Email conversation
        email_convo = [
            (now - timedelta(days=15, hours=11), "I've shared a document with you via Google Drive.", 0, 4),
            (now - timedelta(days=15, hours=11, minutes=45), "Thanks, I'll take a look at it.", 1, 4),
            (now - timedelta(days=12, hours=13), "What did you think of the proposal?", 0, 4),
            (now - timedelta(days=12, hours=13, minutes=30), "It looks good. I made a few comments.", 1, 4),
            (now - timedelta(days=12, hours=13, minutes=45), "Thanks for the feedback!", 0, 4),
            (now - timedelta(days=6, hours=9), "Updated version is now available.", 1, 4),
            (now - timedelta(days=6, hours=9, minutes=20), "Great, I'll review it today.", 0, 4)
        ]
        
        # Combine all conversations
        all_convos = []
        
        for i, msg in enumerate(john_convo):
            all_convos.append((i+1, int((msg[0] - datetime(2001, 1, 1)).total_seconds()), msg[1], msg[2], msg[3]))
            chat_messages.append((1, i+1))
        
        offset = len(john_convo)
        for i, msg in enumerate(sarah_convo):
            all_convos.append((i+offset+1, int((msg[0] - datetime(2001, 1, 1)).total_seconds()), msg[1], msg[2], msg[3]))
            chat_messages.append((2, i+offset+1))
        
        offset += len(sarah_convo)
        for i, msg in enumerate(work_convo):
            all_convos.append((i+offset+1, int((msg[0] - datetime(2001, 1, 1)).total_seconds()), msg[1], msg[2], msg[3]))
            chat_messages.append((3, i+offset+1))
        
        offset += len(work_convo)
        for i, msg in enumerate(email_convo):
            all_convos.append((i+offset+1, int((msg[0] - datetime(2001, 1, 1)).total_seconds()), msg[1], msg[2], msg[3]))
            chat_messages.append((4, i+offset+1))
        
        # Insert messages
        cursor.executemany("INSERT INTO message (rowid, date, text, is_from_me, handle_id) VALUES (?, ?, ?, ?, ?)", all_convos)
        
        # Insert chat-message joins
        cursor.executemany("INSERT INTO chat_message_join (chat_id, message_id) VALUES (?, ?)", chat_messages)
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Sample SMS data generated at {db_path}")
    
    def generate_app_usage_data(self):
        """
        Generate sample app usage data.
        """
        db_path = os.path.join(self.app_usage_dir, "knowledgeC.db")
        
        # Create SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ZOBJECT (
            Z_PK INTEGER PRIMARY KEY,
            Z_ENT INTEGER,
            Z_OPT INTEGER,
            ZSTREAMNAME TEXT,
            ZVALUESTRING TEXT,
            ZSTARTDATE REAL,
            ZENDDATE REAL
        )
        ''')
        
        # Generate sample app usage data
        now = datetime.now()
        app_usage = []
        
        # Common apps
        apps = [
            "com.apple.mobilesafari",  # Safari
            "com.apple.MobileSMS",     # Messages
            "com.apple.mobilemail",    # Mail
            "com.apple.camera",        # Camera
            "com.apple.mobileslideshow",  # Photos
            "com.apple.Maps",          # Maps
            "com.facebook.Facebook",   # Facebook
            "com.instagram.instagram", # Instagram
            "com.atebits.Tweetie2",    # Twitter
            "com.netflix.Netflix",     # Netflix
            "com.spotify.client",      # Spotify
            "com.apple.mobilenotes",   # Notes
            "com.apple.reminders"      # Reminders
        ]
        
        # Generate usage patterns over the last 14 days
        pk = 1
        for day in range(14, -1, -1):
            current_date = now - timedelta(days=day)
            
            # Morning routine (7-9am)
            morning_start = current_date.replace(hour=7, minute=0, second=0)
            
            # Check email
            email_duration = 10 + (pk % 5)  # 10-14 minutes
            app_usage.append((
                pk,
                1,
                1,
                "app.usage",
                "com.apple.mobilemail",
                (morning_start - datetime(2001, 1, 1)).total_seconds(),
                (morning_start + timedelta(minutes=email_duration) - datetime(2001, 1, 1)).total_seconds()
            ))
            pk += 1
            
            # Check social media
            social_start = morning_start + timedelta(minutes=email_duration + 5)
            social_app = apps[6 + (day % 3)]  # Rotate between Facebook, Instagram, Twitter
            social_duration = 15 + (pk % 10)  # 15-24 minutes
            app_usage.append((
                pk,
                1,
                1,
                "app.usage",
                social_app,
                (social_start - datetime(2001, 1, 1)).total_seconds(),
                (social_start + timedelta(minutes=social_duration) - datetime(2001, 1, 1)).total_seconds()
            ))
            pk += 1
            
            # Check messages
            messages_start = social_start + timedelta(minutes=social_duration + 10)
            messages_duration = 5 + (pk % 5)  # 5-9 minutes
            app_usage.append((
                pk,
                1,
                1,
                "app.usage",
                "com.apple.MobileSMS",
                (messages_start - datetime(2001, 1, 1)).total_seconds(),
                (messages_start + timedelta(minutes=messages_duration) - datetime(2001, 1, 1)).total_seconds()
            ))
            pk += 1
            
            # Midday usage (12-2pm)
            midday_start = current_date.replace(hour=12, minute=30, second=0)
            
            # Maps during lunch
            if day % 3 == 0:  # Every 3 days
                maps_duration = 10 + (pk % 5)  # 10-14 minutes
                app_usage.append((
                    pk,
                    1,
                    1,
                    "app.usage",
                    "com.apple.Maps",
                    (midday_start - datetime(2001, 1, 1)).total_seconds(),
                    (midday_start + timedelta(minutes=maps_duration) - datetime(2001, 1, 1)).total_seconds()
                ))
                pk += 1
            
            # Social media again
            social2_start = midday_start + timedelta(minutes=30)
            social2_app = apps[6 + ((day + 1) % 3)]  # Different social app from morning
            social2_duration = 10 + (pk % 8)  # 10-17 minutes
            app_usage.append((
                pk,
                1,
                1,
                "app.usage",
                social2_app,
                (social2_start - datetime(2001, 1, 1)).total_seconds(),
                (social2_start + timedelta(minutes=social2_duration) - datetime(2001, 1, 1)).total_seconds()
            ))
            pk += 1
            
            # Evening usage (6-10pm)
            evening_start = current_date.replace(hour=18, minute=0, second=0)
            
            # Entertainment apps
            if day % 2 == 0:  # Every other day
                netflix_duration = 45 + (pk % 30)  # 45-74 minutes
                app_usage.append((
                    pk,
                    1,
                    1,
                    "app.usage",
                    "com.netflix.Netflix",
                    (evening_start - datetime(2001, 1, 1)).total_seconds(),
                    (evening_start + timedelta(minutes=netflix_duration) - datetime(2001, 1, 1)).total_seconds()
                ))
                pk += 1
            else:
                spotify_duration = 30 + (pk % 20)  # 30-49 minutes
                app_usage.append((
                    pk,
                    1,
                    1,
                    "app.usage",
                    "com.spotify.client",
                    (evening_start - datetime(2001, 1, 1)).total_seconds(),
                    (evening_start + timedelta(minutes=spotify_duration) - datetime(2001, 1, 1)).total_seconds()
                ))
                pk += 1
            
            # More social media
            social3_start = evening_start + timedelta(hours=2)
            social3_app = apps[6 + ((day + 2) % 3)]  # Different social app
            social3_duration = 20 + (pk % 15)  # 20-34 minutes
            app_usage.append((
                pk,
                1,
                1,
                "app.usage",
                social3_app,
                (social3_start - datetime(2001, 1, 1)).total_seconds(),
                (social3_start + timedelta(minutes=social3_duration) - datetime(2001, 1, 1)).total_seconds()
            ))
            pk += 1
            
            # Messages before bed
            messages2_start = current_date.replace(hour=22, minute=0, second=0)
            messages2_duration = 10 + (pk % 10)  # 10-19 minutes
            app_usage.append((
                pk,
                1,
                1,
                "app.usage",
                "com.apple.MobileSMS",
                (messages2_start - datetime(2001, 1, 1)).total_seconds(),
                (messages2_start + timedelta(minutes=messages2_duration) - datetime(2001, 1, 1)).total_seconds()
            ))
            pk += 1
        
        # Insert app usage data
        cursor.executemany(
            "INSERT INTO ZOBJECT (Z_PK, Z_ENT, Z_OPT, ZSTREAMNAME, ZVALUESTRING, ZSTARTDATE, ZENDDATE) VALUES (?, ?, ?, ?, ?, ?, ?)",
            app_usage
        )
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Sample app usage data generated at {db_path}")
    
    def generate_itunes_music_data(self):
        """
        Generate sample iTunes music history data.
        """
        db_path = os.path.join(self.itunes_dir, "iTunes.db")
        
        # Create SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS item (
            id INTEGER PRIMARY KEY,
            title TEXT,
            artist TEXT,
            album TEXT,
            genre TEXT,
            date_added INTEGER,
            play_count INTEGER,
            last_played_date INTEGER,
            media_kind INTEGER
        )
        ''')
        
        # Sample music data
        music_data = [
            # Rock
            ("Bohemian Rhapsody", "Queen", "A Night at the Opera", "Rock", 150, 1),
            ("Stairway to Heaven", "Led Zeppelin", "Led Zeppelin IV", "Rock", 120, 1),
            ("Sweet Child O' Mine", "Guns N' Roses", "Appetite for Destruction", "Rock", 95, 1),
            ("Back in Black", "AC/DC", "Back in Black", "Rock", 85, 1),
            ("Smells Like Teen Spirit", "Nirvana", "Nevermind", "Rock", 110, 1),
            
            # Pop
            ("Shape of You", "Ed Sheeran", "÷", "Pop", 200, 1),
            ("Bad Guy", "Billie Eilish", "When We All Fall Asleep, Where Do We Go?", "Pop", 180, 1),
            ("Uptown Funk", "Mark Ronson ft. Bruno Mars", "Uptown Special", "Pop", 160, 1),
            ("Blinding Lights", "The Weeknd", "After Hours", "Pop", 190, 1),
            ("Shake It Off", "Taylor Swift", "1989", "Pop", 175, 1),
            
            # Hip Hop
            ("Lose Yourself", "Eminem", "8 Mile Soundtrack", "Hip Hop", 140, 1),
            ("Sicko Mode", "Travis Scott", "Astroworld", "Hip Hop", 130, 1),
            ("God's Plan", "Drake", "Scorpion", "Hip Hop", 170, 1),
            ("Alright", "Kendrick Lamar", "To Pimp a Butterfly", "Hip Hop", 100, 1),
            ("Empire State of Mind", "Jay-Z ft. Alicia Keys", "The Blueprint 3", "Hip Hop", 90, 1),
            
            # Electronic
            ("Get Lucky", "Daft Punk ft. Pharrell Williams", "Random Access Memories", "Electronic", 145, 1),
            ("Strobe", "Deadmau5", "For Lack of a Better Name", "Electronic", 80, 1),
            ("Scary Monsters and Nice Sprites", "Skrillex", "Scary Monsters and Nice Sprites", "Electronic", 75, 1),
            ("Levels", "Avicii", "True", "Electronic", 135, 1),
            ("One More Time", "Daft Punk", "Discovery", "Electronic", 125, 1),
            
            # Classical
            ("Moonlight Sonata", "Ludwig van Beethoven", "Beethoven: Piano Sonatas", "Classical", 50, 1),
            ("Four Seasons", "Antonio Vivaldi", "The Four Seasons", "Classical", 40, 1),
            ("Symphony No. 9", "Ludwig van Beethoven", "Beethoven: Symphonies", "Classical", 30, 1),
            ("Clair de Lune", "Claude Debussy", "Suite Bergamasque", "Classical", 45, 1),
            ("Ride of the Valkyries", "Richard Wagner", "Die Walküre", "Classical", 35, 1)
        ]
        
        # Generate play history
        now = datetime.now()
        items = []
        
        for i, (title, artist, album, genre, play_count, media_kind) in enumerate(music_data):
            # Random date added (between 1-3 years ago)
            days_ago_added = 365 + (i * 7) % 730
            date_added = int((now - timedelta(days=days_ago_added)).timestamp())
            
            # Last played date (more recent for higher play counts)
            days_ago_played = max(1, int(365 / (play_count / 50)))
            last_played = int((now - timedelta(days=days_ago_played % 60)).timestamp())
            
            items.append((
                i+1,
                title,
                artist,
                album,
                genre,
                date_added,
                play_count,
                last_played,
                media_kind
            ))
        
        # Insert music data
        cursor.executemany(
            "INSERT INTO item (id, title, artist, album, genre, date_added, play_count, last_played_date, media_kind) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            items
        )
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Sample iTunes music data generated at {db_path}")
    
    def generate_chrome_history_data(self):
        """
        Generate sample Chrome browser history data.
        """
        db_path = os.path.join(self.chrome_dir, "History")
        
        # Create SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            visit_count INTEGER,
            typed_count INTEGER,
            last_visit_time INTEGER
        )
        ''')
        
        # Sample website visits
        websites = [
            # News
            ("https://www.nytimes.com/", "The New York Times - Breaking News, US News, World News", 15, 5),
            ("https://www.cnn.com/", "CNN - Breaking News, Latest News and Videos", 12, 4),
            ("https://www.bbc.com/news", "BBC News - Home", 10, 3),
            ("https://www.reuters.com/", "Reuters - Breaking International News & Views", 8, 2),
            ("https://www.theguardian.com/", "News, sport and opinion from the Guardian's global edition", 7, 2),
            
            # Social Media
            ("https://www.facebook.com/", "Facebook - Log In or Sign Up", 30, 10),
            ("https://www.instagram.com/", "Instagram", 25, 8),
            ("https://twitter.com/", "Twitter", 20, 7),
            ("https://www.linkedin.com/", "LinkedIn: Log In or Sign Up", 15, 5),
            ("https://www.reddit.com/", "Reddit - Dive into anything", 18, 6),
            
            # Shopping
            ("https://www.amazon.com/", "Amazon.com: Online Shopping for Electronics, Apparel, Computers, Books, DVDs & more", 22, 7),
            ("https://www.ebay.com/", "Electronics, Cars, Fashion, Collectibles & More | eBay", 10, 3),
            ("https://www.etsy.com/", "Etsy - Shop for handmade, vintage, custom, and unique gifts for everyone", 8, 2),
            ("https://www.walmart.com/", "Walmart.com | Save Money. Live Better", 6, 1),
            ("https://www.target.com/", "Target : Expect More. Pay Less.", 5, 1),
            
            # Tech
            ("https://www.github.com/", "GitHub: Where the world builds software", 25, 8),
            ("https://stackoverflow.com/", "Stack Overflow - Where Developers Learn, Share, & Build Careers", 20, 6),
            ("https://www.apple.com/", "Apple", 12, 4),
            ("https://www.google.com/search?q=python+tutorial", "python tutorial - Google Search", 15, 5),
            ("https://www.google.com/search?q=javascript+frameworks", "javascript frameworks - Google Search", 10, 3),
            
            # Entertainment
            ("https://www.youtube.com/", "YouTube", 35, 12),
            ("https://www.netflix.com/", "Netflix - Watch TV Shows Online, Watch Movies Online", 20, 6),
            ("https://www.spotify.com/", "Spotify - Web Player: Music for everyone", 18, 5),
            ("https://www.imdb.com/", "IMDb: Ratings, Reviews, and Where to Watch the Best Movies & TV Shows", 12, 4),
            ("https://www.rottentomatoes.com/", "Rotten Tomatoes: Movies | TV Shows | Movie Trailers", 8, 2),
            
            # Travel
            ("https://www.booking.com/", "Booking.com | Official site | The best hotels & accommodations", 10, 3),
            ("https://www.airbnb.com/", "Vacation Homes & Condo Rentals - Airbnb", 8, 2),
            ("https://www.expedia.com/", "Expedia Travel: Vacation Homes, Hotels, Car Rentals, Flights & More", 7, 2),
            ("https://www.tripadvisor.com/", "Tripadvisor: Read Reviews, Compare Prices & Book", 6, 1),
            ("https://www.google.com/maps", "Google Maps", 15, 5)
        ]
        
        # Generate visit history
        now = datetime.now()
        history = []
        
        for i, (url, title, visit_count, typed_count) in enumerate(websites):
            # Last visit time (Windows file time format - microseconds since Jan 1, 1601)
            days_ago = i % 14  # Spread over last 2 weeks
            hours_ago = i % 24
            windows_epoch = datetime(1601, 1, 1)
            last_visit = now - timedelta(days=days_ago, hours=hours_ago)
            microseconds = int((last_visit - windows_epoch).total_seconds() * 1000000)
            
            history.append((
                i+1,
                url,
                title,
                visit_count,
                typed_count,
                microseconds
            ))
        
        # Insert browser history
        cursor.executemany(
            "INSERT INTO urls (id, url, title, visit_count, typed_count, last_visit_time) VALUES (?, ?, ?, ?, ?, ?)",
            history
        )
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Sample Chrome history data generated at {db_path}")


# Test script to run the sample data generator
if __name__ == "__main__":
    output_dir = os.path.join(os.getcwd(), "sample_data")
    generator = SampleDataGenerator(output_dir)
    generator.generate_all_sample_data()
