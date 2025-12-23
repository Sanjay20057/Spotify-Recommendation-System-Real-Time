import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import base64
import os
import sqlite3
import hashlib
from streamlit_cookies_manager import EncryptedCookieManager
import datetime

# ---------------- COOKIE MANAGER ----------------
cookies = EncryptedCookieManager(
    prefix="spotify_clone_",
    password="supersecretpassword123!"
)

if not cookies.ready():
    st.stop()

# ---------------- AUTO LOGIN FROM COOKIE ----------------
logged_in_user = cookies.get("logged_in_user")
login_expiry = cookies.get("login_expiry")

if logged_in_user and login_expiry:
    expiry_time = datetime.datetime.fromisoformat(login_expiry)
    if datetime.datetime.now() < expiry_time:
        st.session_state.logged_in = True
        st.session_state.username = logged_in_user
    else:
        # Expired
        cookies["logged_in_user"] = ""
        cookies["login_expiry"] = ""
        cookies.save()


# ---------- MOBILE DETECTION ----------
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = st.get_option("browser.gatherUsageStats") is None

# ------------------ DATABASE ------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    fav_singer TEXT
)
""")
# ✅ ADD fav_singer column if it does not exist
try:
    c.execute("ALTER TABLE users ADD COLUMN fav_singer TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass


# ---------- LIKED SONGS ----------
c.execute("""
CREATE TABLE IF NOT EXISTS liked_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    track_id TEXT,
    track_name TEXT,
    artist TEXT,
    image TEXT
)
""")

# ---------- PLAYLIST ----------
c.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    playlist_name TEXT,
    track_id TEXT,
    track_name TEXT,
    artist TEXT,
    image TEXT
)
""")

# ---------- USER PROFILE ----------
c.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    username TEXT PRIMARY KEY,
    full_name TEXT,
    bio TEXT,
    image BLOB
)
""")
conn.commit()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(username, password, fav_singer):
    try:
        c.execute(
            "INSERT INTO users (username, password, fav_singer) VALUES (?, ?, ?)",
            (
                username.strip(),              # ✅ exact username
                hash_password(password),
                fav_singer.lower().strip()
            )
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username.strip(), hash_password(password))
    )
    return c.fetchone()

def delete_user(username, password):
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username.strip(), hash_password(password))
    )
    user = c.fetchone()

    if user:
        c.execute("DELETE FROM users WHERE username=?", (username.strip(),))
        conn.commit()
        return True
    return False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "forgot_password" not in st.session_state:
    st.session_state.forgot_password = False

if "allow_reset" not in st.session_state:
    st.session_state.allow_reset = False

# ---------------- SESSION STATE INITIALIZATION ----------------
if "selected_playlist" not in st.session_state:
    st.session_state.selected_playlist = None

import streamlit as st
import base64

# ---------- LOAD LOCAL IMAGE ----------
with open("Login_Background.jpeg", "rb") as f:  # your local file
    data = f.read()
encoded = base64.b64encode(data).decode()  # encode image to base64
import streamlit as st
import base64

# ---------- LOAD LOCAL IMAGE ----------
with open("Login_Background.jpeg", "rb") as f:  # your local file
    data = f.read()
encoded = base64.b64encode(data).decode()  # encode image to base64

# ---------- APPLY AS FULL PAGE BACKGROUND ----------
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpeg;base64,{encoded}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Title */
.login-card h1 {
    color: #00ff66;
    font-size: 32px;
    margin-bottom: 25px;
    text-shadow: 0 0 12px #00ff66;
}

/* Inputs */
div[data-baseweb="input"] > div:first-child {
    border: 2px solid #00ff66 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 8px #00ff66;
    background-color: rgba(26, 26, 26, 0.8) !important;
}
div[data-baseweb="input"] input {
    color: #00ff66 !important;
    font-weight: 600 !important;
    padding: 10px;
}

/* Buttons */
.stButton>button {
    background-color: #00ff66;
    color: black;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    padding: 10px 20px;
    transition: 0.2s;
}
.stButton>button:hover {
    transform: scale(1.05);
    background-color: #00e65c;
}

/* Radio buttons */
[data-baseweb="radio"] > div > label {
    color: #00ff66;
    font-weight: bold;
}

/* Forgot password */
.forgot-btn button {
    background: none;
    color: #00ff66;
    border: none;
    font-weight: bold;
    text-decoration: underline;
}
.forgot-btn button:hover {
    color: black;
    background-color: #00ff66;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOGIN / SIGNUP ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h1>🎧 Welcome To Spotify Clone</h1>", unsafe_allow_html=True)

    auth_mode = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True, key="auth_mode")

    username = st.text_input("Username", placeholder="Enter username", key="login_username")
    password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")

    if auth_mode == "Sign Up":
        fav_singer = st.text_input("Favorite Singer", placeholder="Used for password recovery", key="fav_singer")
        if st.button("Create Account", key="signup_btn"):
            if not fav_singer.strip():
                st.error("Favorite singer required")
            elif signup_user(username, password, fav_singer):
                st.success("Account created! Switch to Login.")
            else:
                st.error("Username already exists")
    else:
        if st.button("Login", key="login_btn"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username

                # Set cookie to expire in 1 day
                expire_time = datetime.datetime.now() + datetime.timedelta(days=1)
                cookies["logged_in_user"] = username
                cookies["login_expiry"] = expire_time.isoformat()
                cookies.save()

                st.rerun()
            else:
                st.error("Invalid username or password")

        # Forgot password button
        st.markdown('<div class="forgot-btn">', unsafe_allow_html=True)
        if st.button("Forgot Password?", key="forgot_btn"):
            st.session_state.forgot_password = True
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

def get_sidebar_profile(username):
    c.execute(
        "SELECT full_name, image FROM user_profile WHERE username=?",
        (username,)
    )
    row = c.fetchone()
    return row if row else ("", None)

# Allow sidebar profile click to open Profile
if "go_profile" not in st.session_state:
    st.session_state.go_profile = False

if st.session_state.go_profile:
    page = "Profile"
    st.session_state.go_profile = False

# ---------- SIDEBAR PROFILE ----------
full_name, profile_img = get_sidebar_profile(st.session_state.username)

display_name = full_name if full_name else st.session_state.username
username_small = f"@{st.session_state.username}"

if profile_img:
    img_base64 = base64.b64encode(profile_img).decode()
    img_src = f"data:image/png;base64,{img_base64}"
else:
    img_src = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"

st.sidebar.markdown(
    f"""
    <style>
    .sidebar-profile {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 15px;
        background: rgba(0, 255, 102, 0.12);
        box-shadow: 0 0 10px #00ff66;
        margin-bottom: 15px;
    }}

    .avatar-wrap {{
        position: relative;
    }}

    .sidebar-profile img {{
        width: 56px;
        height: 56px;
        border-radius: 50%;
        border: 3px solid #00ff66;
        box-shadow: 0 0 12px #00ff66;
        object-fit: cover;
    }}

    .status-dot {{
        position: absolute;
        bottom: 4px;
        right: 4px;
        width: 12px;
        height: 12px;
        background: #00ff66;
        border-radius: 50%;
        border: 2px solid #0d0d0d;
        box-shadow: 0 0 8px #00ff66;
    }}

    .sidebar-text {{
        display: flex;
        flex-direction: column;
        line-height: 1.1;
    }}

    .sidebar-name {{
        color: #00ff66;
        font-size: 18px;
        font-weight: 700;
    }}

    .sidebar-username {{
        color: #aaa;
        font-size: 12px;
    }}
    </style>

    <div class="sidebar-profile">
        <div class="avatar-wrap">
            <img src="{img_src}">
            <div class="status-dot"></div>
        </div>
        <div class="sidebar-text">
            <div class="sidebar-name">{display_name}</div>
            <div class="sidebar-username">{username_small}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Menu",
    ["Search Music", "Liked Songs", "Playlists", "Profile"],
    key="main_menu"
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    cookies["logged_in_user"] = ""
    cookies["login_expiry"] = ""
    cookies.save()
    st.rerun()


def like_song(username, track):
    c.execute("""
        INSERT OR IGNORE INTO liked_songs
        (username, track_id, track_name, artist, image)
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        track["id"],
        track["name"],
        track["artists"][0]["name"],
        track["album"]["images"][0]["url"]
    ))
    conn.commit()


def is_song_liked(username, track_id):
    c.execute(
        "SELECT 1 FROM liked_songs WHERE username=? AND track_id=?",
        (username, track_id)
    )
    return c.fetchone() is not None


def unlike_song(username, track_id):
    c.execute(
        "DELETE FROM liked_songs WHERE username=? AND track_id=?",
        (username, track_id)
    )
    conn.commit()


def add_to_playlist(username, playlist, track):
    c.execute("""
        INSERT INTO playlists
        (username, playlist_name, track_id, track_name, artist, image)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        playlist,
        track["id"],
        track["name"],
        track["artists"][0]["name"],
        track["album"]["images"][0]["url"]
    ))
    conn.commit()

def remove_from_playlist(username, playlist_name, track_id):
    c.execute(
        "DELETE FROM playlists WHERE username=? AND playlist_name=? AND track_id=?",
        (username, playlist_name, track_id)
    )
    conn.commit()

def get_profile(username):
    c.execute(
        "SELECT full_name, bio, image FROM user_profile WHERE username=?",
        (username,)
    )
    return c.fetchone()

def save_profile(username, full_name, bio, image_bytes):
    c.execute("""
        INSERT INTO user_profile (username, full_name, bio, image)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
        full_name=excluded.full_name,
        bio=excluded.bio,
        image=excluded.image
    """, (username, full_name, bio, image_bytes))
    conn.commit()

def spotify_playlist_player(track_ids):
    ids = ",".join(track_ids)
    return f"""
    <iframe
        src="https://open.spotify.com/embed/playlist/{ids}"
        width="100%"
        height="380"
        frameborder="0"
        allow="encrypted-media"
        style="border-radius:14px;">
    </iframe>
    """

# GIF BACKGROUND
def add_bg_gif(gif_file):
    if os.path.exists(gif_file):
        with open(gif_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            body {{
                background: url("data:image/gif;base64,{encoded}") no-repeat center center fixed;
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: #0d0d0d;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

add_bg_gif("background.gif")

st.markdown(
    """
    <style>
    .stApp {
        background: url("https://wallpapers.com/images/hd/pure-black-background-py9pa0f1mlsscm9s.jpg") center center fixed;
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# SPOTIFY AUTH
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=st.secrets["CLIENT_ID"],
        client_secret=st.secrets["CLIENT_SECRET"]
    )
)

# ARTIST SEARCH
def get_clean_artist_result(query):
    res = sp.search(q=query, type="artist", limit=10)
    artists = res["artists"]["items"]

    if not artists:
        return None

    q = query.lower()

    # 1️⃣ Exact match
    for a in artists:
        if a["name"].lower() == q:
            return a

    # 2️⃣ Starts with match
    for a in artists:
        if a["name"].lower().startswith(q):
            return a

    # 3️⃣ Contains match
    for a in artists:
        if q in a["name"].lower():
            return a

    # 4️⃣ Fallback — highest popularity
    return sorted(artists, key=lambda x: x["popularity"], reverse=True)[0]

if "album_expand" not in st.session_state:
    st.session_state.album_expand = {}

if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

st.session_state.is_mobile = st.get_option("browser.gatherUsageStats") is None

def spotify_player(track_id):
    height = 80 if st.session_state.is_mobile else 80
    return f"""
    <iframe
        src="https://open.spotify.com/embed/track/{track_id}?theme=0"
        width="100%"
        height="{height}"
        frameborder="0"
        allow="encrypted-media"
        style="border-radius:12px;">
    </iframe>
    """

def spotify_album_tracks_player(album_id):
    album_tracks = sp.album_tracks(album_id)["items"]  # Get tracks from the album
    players = ""
    for track in album_tracks[:5]:  # Show first 5 tracks as embedded players
        track_id = track["id"]
        players += f"""
        <iframe
            src="https://open.spotify.com/embed/track/{track_id}?theme=0"
            width="100%"
            height="80"
            frameborder="0"
            allow="encrypted-media"
            style="border-radius:12px; margin-top:8px;">
        </iframe>
        """
    return players


# ARTIST HEADER
def show_artist_header(song_query, results):
    try:
        artist = get_clean_artist_result(song_query)

        # If query was actually a song → find artist from song
        if artist is None:
            track = results["tracks"]["items"][0]
            artist_id = track["artists"][0]["id"]
            artist = sp.artist(artist_id)

        # Extract artist info
        artist_name = artist["name"]
        followers = f"{artist['followers']['total']:,}"
        popularity = artist.get("popularity", 0)
        genres = ", ".join(artist.get("genres", [])[:5]) or "Not Available"

        if artist.get("images"):
            artist_img = artist["images"][0]["url"]
        else:
            artist_img = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

        # ------- UI SECTION (Unchanged) --------
        st.markdown(f"""
        <style>
        .artist-banner {{
            width: 100%;
            padding: 35px;
            border-radius: 18px;
            background: linear-gradient(135deg, #003300, #00cc66, #00994d);
            display: flex;
            align-items: center;
            gap: 25px;
            box-shadow: 0 0 20px #00ff66;
            margin-bottom: 30px;
        }}
        .artist-img {{
            width: 160px;
            height: 160px;
            border-radius: 50%;
            border: 4px solid #00ff66;
            box-shadow: 0 0 25px #00ff66;
        }}
        .artist-name {{
            font-size: 48px;
            font-weight: 700;
            color: white;
        }}
        .artist-meta {{
            color: #d4d4d4;
            font-size: 18px;
            margin-top: 6px;
        }}
        </style>
        """, unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="artist-banner">
                <img src="{artist_img}" class="artist-img">
                <div>
                    <div class="artist-name">{artist_name}</div>
                    <div class="artist-meta">Followers: {followers}</div>
                    <div class="artist-meta">Popularity: {popularity} / 100</div>
                    <div class="artist-meta">Genres: {genres}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------- TOP TRACKS ----------------
        top_tracks = sp.artist_top_tracks(artist["id"])["tracks"][:5]
        st.markdown("<h2 style='color:#00ff66;'>🔥 Top Tracks</h2>", unsafe_allow_html=True)

        cols = st.columns(2 if st.session_state.get("is_mobile", False) else 5)
        for i, track in enumerate(top_tracks):
            img = track["album"]["images"][0]["url"]
            name = track["name"]
            track_id = track["id"]

            with cols[i]:
                st.markdown("<div class='song-card'>", unsafe_allow_html=True)

                st.markdown(
                    f"<img src='{img}' class='glow-img' style='width:100%;'>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<p class='song-title'>{name}</p>",
                    unsafe_allow_html=True
                )

                # ✅ PLAYABLE SPOTIFY TRACK
                st.markdown(
                    spotify_player(track_id),
                    unsafe_allow_html=True
                )

                st.markdown("</div>", unsafe_allow_html=True)


    except Exception as e:
        st.error(f"Artist load error: {e}")

# SHOW SONG HEADER (FOR SONG SEARCH)
def show_song_header(track):
    try:
        song_name = track["name"]
        artist_name = track["artists"][0]["name"]
        img = track["album"]["images"][0]["url"]

        st.markdown(f"""
            <h2 style='color:#00ff66;'>🎵 Song Result</h2>
            <div class="neon-song-header">
                <img src="{img}">
                <div class="neon-song-info">
                    <div class="title">{song_name}</div>
                    <div class="artist">Artist: {artist_name}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(spotify_player(track["id"]), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Song header error: {e}")

def show_album_header(album):
    img = album["images"][0]["url"] if album["images"] else ""
    name = album["name"]
    artist = album["artists"][0]["name"]

    # total tracks (comes directly from album object)
    total_tracks = album.get("total_tracks", "N/A")

    st.markdown(f"""
    <div class="neon-song-header">
        <img src="{img}">
        <div class="neon-song-info">
            <div class="title">{name}</div>
            <div class="artist">Artist: {artist}</div>
            <div class="artist">Tracks: {total_tracks} songs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# SEARCH FUNCTION
def search_top_10(song_name):
    results = sp.search(q=song_name, type="track", limit=10)
    data = []
    for item in results["tracks"]["items"]:
        data.append({
            "track_name": item["name"],
            "artist": item["artists"][0]["name"],
            "album": item["album"]["name"],
            "popularity": item["popularity"],
            "image": item["album"]["images"][0]["url"],
            "spotify_url": item["external_urls"]["spotify"],
            "id": item["id"]
        })
    return pd.DataFrame(data), results



# UI STYLING (UNCHANGED)
image_path = "WhatsApp Image 2025-12-03 at 20.47.25_382aee0c.jpg"

with open(image_path, "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data).decode()

st.markdown(f"""
<div style="text-align:left; margin-top:-120px; margin-bottom:-100px;">
    <img src="data:image/jpeg;base64,{b64}" width="170">
</div>
""", unsafe_allow_html=True)



st.markdown("""
<style>

body { color: white; }

/* -----------------------------
     SPOTIFY LINK BUTTON
------------------------------ */
.spotify-link {
    color: #00ff66 !important;
    font-weight: 700;
    font-size: 18px;
    text-decoration: none !important;
    padding: 8px 14px;
    border: 2px solid #00ff66;
    border-radius: 10px;
    display: inline-block;
    margin-top: 8px;
    transition: 0.3s ease;
}
.spotify-link:hover {
    background-color: #00ff66;
    color: black !important;
    transform: scale(1.05);
    box-shadow: 0 0 12px #00ff66;
}

/* -----------------------------
     SMALL PLAY BUTTON
------------------------------ */
.spotify-play {
    color: #00ff66 !important;
    font-weight: 700;
    font-size: 16px;
    text-decoration: none !important;
    padding: 6px 12px;
    border: 2px solid #00ff66;
    border-radius: 10px;
    display: inline-block;
    margin-top: 6px;
    transition: 0.3s ease;
}
.spotify-play:hover {
    background-color: #00ff66;
    color: black !important;
    transform: scale(1.05);
    box-shadow: 0 0 12px #00ff66;
}

/* -----------------------------
     TEXT INPUT FIX
------------------------------ */

/* Remove outer border (prevents double border) */
div[data-baseweb="input"] {
    border: none !important;
}

/* Real neon input */
div[data-baseweb="input"] > div:first-child {
    border: 2px solid #00ff66 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 8px #00ff66;
    background-color: #1a1a1a !important;
}

div[data-baseweb="input"] input {
    color: #00ff66 !important;
    font-weight: 600 !important;
    padding: 10px;
}

/* -----------------------------
     SELECTBOX (MATCH SAME UI)
------------------------------ */
div[data-baseweb="select"] {
    border: none !important;
}

/* Neon border only on core box */
div[data-baseweb="select"] > div:first-child {
    border: 2px solid #00ff66 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 8px #00ff66;
    color: #00ff66 !important;
    background-color: #1a1a1a !important;
}

/* Dropdown arrow */
div[data-baseweb="select"] svg {
    fill: #00ff66 !important;
}

/* Dropdown list */
ul[role="listbox"] li {
    background-color: #111 !important;
    color: #00ff66 !important;
}
ul[role="listbox"] li:hover {
    background-color: #00ff66 !important;
    color: black !important;
}

/* -----------------------------
     BUTTONS
------------------------------ */
.stButton>button {
    background-color: #00ff66;
    color: black;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    padding: 10px 20px;
    transition: 0.2s;
}
.stButton>button:hover {
    transform: scale(1.05);
    background-color: #00e65c;
}

/* -----------------------------
     SONG CARD + IMAGE GLOW
------------------------------ */
.song-card {
    border: 2px solid #00ff66;
    padding: 15px;
    border-radius: 15px;
    background-color: rgba(17, 17, 17, 0.8);
    transition: transform 0.3s, box-shadow 0.3s;
    margin-bottom: 20px;
}
.song-card:hover {
    box-shadow: 0 0 12px #00ff66;
}

.song-title {
    color: #00ff66;
    font-weight: bold;
    font-size: 20px;
    margin-top: 10px;
}

.glow-img {
    border-radius: 20px;
    border: 3px solid #00ff66;
    box-shadow: 0 0 8px #00ff66, 0 0 15px #00ff66;
    transition: 0.25s ease;
    margin-bottom: 12px;
}
.glow-img:hover {
    transform: scale(1.03);
    box-shadow: 0 0 12px #00ff66, 0 0 20px #00ff66;
}

/* -------- BIG SPOTIFY DURATION BAR -------- */
.spotify-big {
    overflow: hidden;
    height: 70px;              /* BIGGER interaction area */
    border-radius: 14px;
    margin-top: 10px;
    box-shadow: 0 0 10px #00ff66;
}

.spotify-big iframe {
    margin-top: 0;
}

/* -----------------------------
     NEON SONG HEADER
------------------------------ */
.neon-song-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px;
    border: 2px solid #00ff66;
    border-radius: 18px;
    background-color: rgba(17, 17, 17, 0.85);
    box-shadow: 0 0 25px #00ff66;
    animation: neon-glow 1.5s ease-in-out infinite alternate;
    margin-bottom: 20px;
}

.neon-song-header img {
    width: 150px;
    height: 150px;
    border-radius: 12px;
    border: 3px solid #00ff66;
    box-shadow: 0 0 15px #00ff66;
    transition: transform 0.3s, box-shadow 0.3s;
}

.neon-song-header img:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px #00ff66;
}

.neon-song-info {
    display: flex;
    flex-direction: column;
    color: white;
}

.neon-song-info .title {
    font-size: 26px;
    font-weight: bold;
    color: #00ff66;
    margin-bottom: 6px;
}

.neon-song-info .artist {
    font-size: 18px;
    color: white;
}

@keyframes neon-glow {
    0% { box-shadow: 0 0 10px #00ff66; }
    50% { box-shadow: 0 0 25px #00ff66; }
    100% { box-shadow: 0 0 10px #00ff66; }
}

/* -----------------------------
   MOBILE RESPONSIVE FIX
------------------------------ */
@media (max-width: 768px) {

    /* Artist banner */
    .artist-banner {
        flex-direction: column;
        text-align: center;
        padding: 18px;
    }

    .artist-img {
        width: 110px;
        height: 110px;
    }

    .artist-name {
        font-size: 28px;
    }

    .artist-meta {
        font-size: 14px;
    }

    /* Neon song header */
    .neon-song-header {
        flex-direction: column;
        gap: 12px;
        padding: 15px;
    }

    .neon-song-header img {
        width: 120px;
        height: 120px;
    }

    .neon-song-info .title {
        font-size: 20px;
        text-align: center;
    }

    .neon-song-info .artist {
        font-size: 14px;
        text-align: center;
    }

    /* Song cards */
    .song-card {
        padding: 12px;
    }

    .song-title {
        font-size: 16px;
        text-align: center;
    }

    /* Spotify iframe fix */
    iframe {
        height: 80px !important;
    }
}

/* Force Streamlit columns to stack on mobile */
@media (max-width: 768px) {
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
}

@media (max-width: 768px){
    /* Stack song cards */
    .song-card { padding: 10px; }
    .song-title { font-size: 16px; }

    /* Neon song header */
    .neon-song-header { flex-direction: column; gap:12px; padding:15px; }
    .neon-song-header img { width: 120px; height: 120px; }
    .neon-song-info .title { font-size: 18px; text-align:center; }
    .neon-song-info .artist { font-size: 14px; text-align:center; }

    /* Playlist cards */
    div.playlist-card { width: 100% !important; max-width: 320px; }

    /* Sidebar */
    .sidebar-profile { flex-direction: column; align-items:center; text-align:center; }
    .sidebar-name { font-size:16px; }
    .sidebar-username { font-size:12px; }

    /* Buttons */
    .stButton>button { width:100%; margin-bottom:8px; }

    /* Inputs */
    div[data-baseweb="input"] > div:first-child { width:100% !important; }

    /* Iframes */
    iframe { width:100% !important; }
}

</style>
""", unsafe_allow_html=True)

if page == "Search Music":
    st.warning(
        "🎵 Only previews are available unless you are logged into Spotify Premium in this browser."
    )

    # SEARCH INPUT
    st.write("### Search any Song, Album or Artist")
    song = st.text_input("Enter song, artist, or album:")


    # Detect if user searched song or artist
    def detect_search_type(query):
        res = sp.search(q=query, type="track,artist", limit=3)

        tracks = res.get("tracks", {}).get("items", [])
        artists = res.get("artists", {}).get("items", [])

        if tracks:
            return "song", tracks[0]
        elif artists:
            return "artist", artists[0]
        else:
            return None, None


    def is_artist_query(q):
        artist = get_clean_artist_result(q)
        return artist is not None


    # FILTER OPTION
    search_filter = st.selectbox(
        "Choose what you want to search:",
        ["Song", "Artist", "Album"]
    )

    # SEARCH BUTTON
    if st.button("Search"):
        st.session_state.search_clicked = True

    if st.session_state.search_clicked and song.strip():

        with st.spinner("Searching Spotify..."):

            # SONG SEARCH
            if search_filter == "Song":
                results = sp.search(q=song, type="track", limit=10)
                tracks = results["tracks"]["items"]

                if not tracks:
                    st.error("No songs found.")
                    st.stop()

                # Show first song header
                show_song_header(tracks[0])

                # Show all artists of the song
                st.markdown("<h2 style='color:#00ff66;'>🎤 Artist(s)</h2>", unsafe_allow_html=True)
                for art in tracks[0]["artists"]:
                    artist_full = sp.artist(art["id"])
                    show_artist_header(artist_full["name"], results)

                # Recommendation list (your table)
                df, res = search_top_10(song)
                st.success(f"Showing top {len(df)} similar songs 🎶")

                cols_per_row = 1 if st.session_state.is_mobile else 5  # for top tracks or search results
                cols = st.columns(cols_per_row)

                for i, row in df.iterrows():
                    with cols[i % 5]:
                        st.markdown("<div class='song-card'>", unsafe_allow_html=True)
                        st.markdown(f"<img src='{row['image']}' class='glow-img' style='width:100%;'>",
                                    unsafe_allow_html=True)
                        st.markdown(f"<p class='song-title'>{row['track_name']}</p>", unsafe_allow_html=True)
                        st.write(f"**Artist:** {row['artist']}")
                        st.write(f"**Album:** {row['album']}")
                        st.write(f"**Popularity:** {row['popularity']}")
                        st.markdown(spotify_player(row["id"]), unsafe_allow_html=True)
                        col1, col2 = st.columns(2)

                        with col1:
                            liked = is_song_liked(st.session_state.username, row["id"])

                            if liked:
                                if st.button("💔 Unlike", key=f"remove_{row['id']}"):
                                    unlike_song(st.session_state.username, row["id"])
                                    st.rerun()
                            else:
                                if st.button("❤️ Like", key=f"like_{row['id']}"):
                                    like_song(st.session_state.username, {
                                        "id": row["id"],
                                        "name": row["track_name"],
                                        "artists": [{"name": row["artist"]}],
                                        "album": {"images": [{"url": row["image"]}]}
                                    })
                                    st.rerun()

                        with col2:
                            # ---- EXISTING PLAYLIST SELECT ----
                            playlist_list = c.execute("""
                                SELECT DISTINCT playlist_name
                                FROM playlists
                                WHERE username=? AND playlist_name!=''
                            """, (st.session_state.username,)).fetchall()

                            playlist_names = [p[0] for p in playlist_list]

                            if playlist_names:
                                selected_playlist = st.selectbox(
                                    "Add to Playlist",
                                    playlist_names,
                                    key=f"select_pl_{row['id']}"
                                )

                                if st.button("➕ Add", key=f"add_{row['id']}"):
                                    add_to_playlist(
                                        st.session_state.username,
                                        selected_playlist,
                                        {
                                            "id": row["id"],
                                            "name": row["track_name"],
                                            "artists": [{"name": row["artist"]}],
                                            "album": {"images": [{"url": row["image"]}]}
                                        }
                                    )
                                    st.success(f"Added to '{selected_playlist}'")
                            else:
                                st.info("Create a playlist first")

                        st.markdown("</div>", unsafe_allow_html=True)

            # ARTIST SEARCH
            elif search_filter == "Artist":
                artist = get_clean_artist_result(song)

                if not artist:
                    st.error("No artist found.")
                    st.stop()

                show_artist_header(song_query=song, results={})

                # Recommended tracks by artist
                df, res = search_top_10(song)
                st.success(f"Showing top {len(df)} similar songs 🎶")

                cols_per_row = 1 if st.session_state.is_mobile else 5  # for top tracks or search results
                cols = st.columns(cols_per_row)

                for i, row in df.iterrows():
                    with cols[i % 5]:
                        st.markdown("<div class='song-card'>", unsafe_allow_html=True)
                        st.markdown(f"<img src='{row['image']}' class='glow-img' style='width:100%;'>",
                                    unsafe_allow_html=True)
                        st.markdown(f"<p class='song-title'>{row['track_name']}</p>", unsafe_allow_html=True)
                        st.write(f"**Artist:** {row['artist']}")
                        st.write(f"**Album:** {row['album']}")
                        st.write(f"**Popularity:** {row['popularity']}")
                        st.markdown(spotify_player(row["id"]), unsafe_allow_html=True)
                        col1, col2 = st.columns(2)

                        with col1:
                            liked = is_song_liked(st.session_state.username, row["id"])

                            if liked:
                                if st.button("💔 Unlike", key=f"remove_{row['id']}"):
                                    unlike_song(st.session_state.username, row["id"])
                                    st.rerun()
                            else:
                                if st.button("❤️ Like", key=f"like_{row['id']}"):
                                    like_song(st.session_state.username, {
                                        "id": row["id"],
                                        "name": row["track_name"],
                                        "artists": [{"name": row["artist"]}],
                                        "album": {"images": [{"url": row["image"]}]}
                                    })
                                    st.rerun()

                        with col2:
                            # ---- EXISTING PLAYLIST SELECT ----
                            playlist_list = c.execute("""
                                SELECT DISTINCT playlist_name
                                FROM playlists
                                WHERE username=? AND playlist_name!=''
                            """, (st.session_state.username,)).fetchall()

                            playlist_names = [p[0] for p in playlist_list]

                            if playlist_names:
                                selected_playlist = st.selectbox(
                                    "Add to Playlist",
                                    playlist_names,
                                    key=f"select_pl_{row['id']}"
                                )

                                if st.button("➕ Add", key=f"add_{row['id']}"):
                                    add_to_playlist(
                                        st.session_state.username,
                                        selected_playlist,
                                        {
                                            "id": row["id"],
                                            "name": row["track_name"],
                                            "artists": [{"name": row["artist"]}],
                                            "album": {"images": [{"url": row["image"]}]}
                                        }
                                    )
                                    st.success(f"Added to '{selected_playlist}'")
                            else:
                                st.info("Create a playlist first")

                        st.markdown("</div>", unsafe_allow_html=True)

            # ALBUM SEARCH
            elif search_filter == "Album":

                albums = sp.search(q=song, type="album", limit=5)["albums"]["items"]

                if not albums:
                    st.error("No albums found.")
                    st.stop()

                st.markdown("<h2 style='color:#00ff66;'>💿 Albums</h2>", unsafe_allow_html=True)

                for album in albums:

                    album_id = album["id"]

                    show_album_header(album)

                    tracks = sp.album_tracks(album_id)["items"]
                    TOTAL = len(tracks)
                    LIMIT = 5

                    # init state
                    if album_id not in st.session_state.album_expand:
                        st.session_state.album_expand[album_id] = False

                    expanded = st.session_state.album_expand[album_id]

                    # decide visible tracks
                    visible_tracks = tracks if expanded else tracks[:LIMIT]

                    # render tracks
                    for track in visible_tracks:
                        st.markdown(
                            spotify_player(track["id"]),
                            unsafe_allow_html=True
                        )

                    # ---- BUTTON (THIS IS THE FIX) ----
                    if TOTAL > LIMIT:
                        label = "➖ Show Less" if expanded else f"➕ Show More ({TOTAL - LIMIT})"

                        if st.button(label, key=f"btn_{album_id}"):
                            st.session_state.album_expand[album_id] = not expanded
                            st.rerun()  # 🚀 THIS IS CRITICAL

                    st.markdown(
                        "<hr style='border:1px solid #00ff66; margin:30px 0;'>",
                        unsafe_allow_html=True
                    )

if page == "Profile":

    st.markdown(
        f"<h1 style='color:#00ff66; text-align:Left;'>👤 {st.session_state.username}</h1>",
        unsafe_allow_html=True
    )

    profile = get_profile(st.session_state.username)
    full_name = profile[0] if profile else ""
    bio = profile[1] if profile else ""
    img_data = profile[2] if profile else None

    # --- MAIN PROFILE LAYOUT ---
    col1, col2 = st.columns([1,2] if not st.session_state.is_mobile else [1,1])

    # -------- PROFILE IMAGE --------
    with col1:
        # Determine image to display
        if img_data:
            img_base64 = base64.b64encode(img_data).decode()
            img_src = f"data:image/png;base64,{img_base64}"
        else:
            img_src = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"

        st.markdown(
            f"""
            <div style="
                display:flex;
                justify-content:center;
                align-items:center;
                border:3px solid #00ff66;
                border-radius:50%;
                width:180px;
                height:180px;
                overflow:hidden;
                box-shadow: 0 0 12px #00ff66;">
                <img src="{img_src}" style="width:100%; height:100%; object-fit:cover;">
            </div>
            """,
            unsafe_allow_html=True
        )

        # Upload new image
        uploaded_img = st.file_uploader(
            "Change Profile Image",
            type=["png", "jpg", "jpeg"]
        )

        # Remove image button
        if img_data:
            if st.button("🗑 Remove Image"):
                img_data = None  # remove current image
                save_profile(st.session_state.username, full_name, bio, None)
                st.success("Profile image removed!")
                st.rerun()

    # -------- PROFILE DETAILS --------
    with col2:
        new_name = st.text_input("Full Name", value=full_name)
        new_bio = st.text_area("Bio", value=bio, height=140)

        st.markdown(
            """
            <style>
            .save-btn button {
                background-color: #00ff66 !important;
                color: black !important;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                transition: 0.2s;
            }
            .save-btn button:hover {
                transform: scale(1.05);
                background-color: #00e65c !important;
                box-shadow: 0 0 15px #00ff66;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        if st.button("💾 Save Profile"):
            image_bytes = img_data
            if uploaded_img:
                image_bytes = uploaded_img.read()

            save_profile(
                st.session_state.username,
                new_name,
                new_bio,
                image_bytes
            )
            st.success("Profile updated successfully 🎉")
            st.rerun()

    # -------- PROFILE METADATA --------
    st.markdown(
        f"""
        <div style='margin-top:30px; padding:20px; border:2px solid #00ff66; border-radius:18px; background:rgba(17,17,17,0.85); box-shadow:0 0 20px #00ff66;'>
            <h3 style='color:#00ff66;'>Account Information</h3>
            <p style='color:white;'><strong>Username:</strong> {st.session_state.username}</p>
            <p style='color:white;'><strong>Full Name:</strong> {new_name if new_name else 'N/A'}</p>
            <p style='color:white;'><strong>Bio:</strong> {new_bio if new_bio else 'N/A'}</p>
            <p style='color:#aaa;'>Account Type: Local Spotify App User</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ---------------- DELETE ACCOUNT ----------------
    st.markdown("---")

    # initialize state
    if "show_delete" not in st.session_state:
        st.session_state.show_delete = False

    # STEP 1: show only button
    if not st.session_state.show_delete:
        if st.button("❌ Delete Account"):
            st.session_state.show_delete = True

    # STEP 2: show confirmation form after click
    else:
        st.markdown("### ⚠️ Delete Account Permanently")

        del_username = st.text_input("Confirm Username")
        del_password = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Delete Permanently"):
                if delete_user(del_username, del_password):
                    st.success("Account deleted permanently")

                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.show_delete = False
                    st.rerun()
                else:
                    st.error("Incorrect username or password")

        with col1:
            if st.button("Cancel"):
                st.session_state.show_delete = False

if page == "Liked Songs":

    st.markdown(
        "<h1 style='color:#00ff66;'>▶️ Liked Songs</h1>",
        unsafe_allow_html=True
    )

    # Fetch liked songs
    liked_songs = c.execute("""
        SELECT track_id, track_name, artist
        FROM liked_songs
        WHERE username=?
    """, (st.session_state.username,)).fetchall()

    if not liked_songs:
        st.info("You have no liked songs yet.")
        st.stop()

    # Map display name to track_id for selection
    track_options = {f"{track_name} - {artist}": track_id for track_id, track_name, artist in liked_songs}

    # Multi-select for removal
    tracks_to_remove = st.multiselect(
        "Select songs to remove from liked songs",
        options=list(track_options.keys())
    )

    # Remove button
    if st.button("❌ Unlike Selected Songs"):
        if tracks_to_remove:
            for track in tracks_to_remove:
                track_id = track_options[track]
                c.execute("""
                    DELETE FROM liked_songs
                    WHERE username=? AND track_id=?
                """, (st.session_state.username, track_id))
            conn.commit()
            st.success(f"Removed {len(tracks_to_remove)} song(s) from Liked Songs")
            st.rerun()
        else:
            st.warning("No songs selected to like.")

    st.markdown("<h4 style='color:#00ff66;'>🎧 Your Liked Songs</h4>", unsafe_allow_html=True)

    # Display playable tracks
    for track_id, track_name, artist in liked_songs:
        st.markdown(f"**{track_name} - {artist}**", unsafe_allow_html=True)
        st.markdown(
            spotify_player(track_id),
            unsafe_allow_html=True
        )




if page == "Playlists":
    st.markdown("<h1 style='color:#00ff66;'>🎶 My Playlists</h1>", unsafe_allow_html=True)

    playlists = c.execute("""
        SELECT DISTINCT playlist_name
        FROM playlists
        WHERE username=? AND playlist_name IS NOT NULL AND playlist_name != ''
    """, (st.session_state.username,)).fetchall()

    # Filter out any invalid entries just in case
    playlists = [pl for pl in playlists if pl[0] and pl[0].strip() != ""]

    # --- Create Playlist ---
    st.markdown("<h3 style='color:#00ff66;'>➕ Create New Playlist</h3>", unsafe_allow_html=True)
    new_pl_name = st.text_input("Playlist Name", key="new_playlist_input")
    if st.button("Create Playlist"):
        if new_pl_name.strip() != "":
            # Insert dummy entry to create playlist structure
            c.execute("""
                INSERT OR IGNORE INTO playlists (username, playlist_name, track_id, track_name, artist, image)
                VALUES (?, ?, '', '', '', '')
            """, (st.session_state.username, new_pl_name))
            conn.commit()
            st.success(f"Playlist '{new_pl_name}' created!")
            st.rerun()
        else:
            st.error("Playlist name cannot be empty.")

    # --- Playlist Cards ---
    if st.session_state.selected_playlist is None:
        st.markdown("<div style='display:flex; flex-wrap:wrap; gap:15px; justify-content:center;'>", unsafe_allow_html=True)

        # Number of columns per row
        cols_per_row = 3
        cols = st.columns(cols_per_row)

        for i, pl in enumerate(playlists):
            pl_name = pl[0]
            col = cols[i % cols_per_row]  # Assign column cyclically
            with col:
                # Playlist card click
                if st.button(f"🎵 {pl_name}", key=f"pl_card_{pl_name}", help="Click to open playlist"):
                    st.session_state.selected_playlist = pl_name
                    st.rerun()

                # Playlist card UI (visual)
                st.markdown(
                    f"""
                    <div style="
                        width:180px;
                        height:180px;
                        border:2px solid #00ff66;
                        border-radius:18px;
                        display:flex;
                        flex-direction:column;
                        align-items:center;
                        justify-content:center;
                        background:linear-gradient(135deg, #003300, #00cc66, #00994d);
                        color:white;
                        font-weight:bold;
                        font-size:20px;
                        text-align:center;
                        box-shadow:0 0 15px #00ff66;
                        cursor:pointer;
                        margin-bottom:10px;
                        ">
                        🎵<br>{pl_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Delete playlist button
                if st.button(f"🗑 Delete {pl_name}", key=f"delete_{pl_name}"):
                    c.execute("""
                        DELETE FROM playlists
                        WHERE username=? AND playlist_name=?
                    """, (st.session_state.username, pl_name))
                    conn.commit()
                    st.success(f"Playlist '{pl_name}' deleted!")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Playlist Detail Page ---
    # Fetch only valid songs (track_id not empty or None)
    songs = c.execute("""
        SELECT track_id, track_name, artist
        FROM playlists
        WHERE username=? AND playlist_name=? AND track_id IS NOT NULL AND track_id != ''
    """, (st.session_state.username, st.session_state.selected_playlist)).fetchall()

    if not songs:
        st.info("No songs in this playlist.")
    else:
        # Map display name to track_id
        track_options = {f"{track_name} - {artist}": track_id for track_id, track_name, artist in songs}

        # Multi-select widget for removal
        tracks_to_remove = st.multiselect(
            "Select songs to remove",
            options=list(track_options.keys())
        )

        # Display playable songs
        st.markdown("<h4 style='color:#00ff66;'>🎧 Playlist Songs</h4>", unsafe_allow_html=True)
        for track_id, track_name, artist in songs:
            st.markdown(f"**{track_name} - {artist}**", unsafe_allow_html=True)
            st.markdown(
                spotify_player(track_id),
                unsafe_allow_html=True
            )

        # Remove selected songs button
        if st.button("❌ Remove Selected Songs"):
            if tracks_to_remove:
                for track in tracks_to_remove:
                    track_id = track_options[track]
                    # DELETE from playlists table instead of liked_songs
                    c.execute("""
                        DELETE FROM playlists
                        WHERE username=? AND playlist_name=? AND track_id=?
                    """, (st.session_state.username, st.session_state.selected_playlist, track_id))
                conn.commit()
                st.success(f"Removed {len(tracks_to_remove)} song(s) from '{st.session_state.selected_playlist}'")
                st.rerun()
            else:
                st.warning("No songs selected to remove.")

    if st.button("⬅ Back to Playlists"):
        st.session_state.selected_playlist = None
        st.rerun()

