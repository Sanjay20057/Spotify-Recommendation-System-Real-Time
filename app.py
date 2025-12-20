import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import base64
import os

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
    return f"""
    <iframe
        src="https://open.spotify.com/embed/track/{track_id}?theme=0"
        width="100%"
        height="80"
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
st.image("WhatsApp Image 2025-12-03 at 20.47.25_382aee0c.jpg", width=170)

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
</style>
""", unsafe_allow_html=True)


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

            cols = st.columns(2 if st.session_state.get("is_mobile", False) else 5)
            for i, row in df.iterrows():
                with cols[i % 5]:
                    st.markdown("<div class='song-card'>", unsafe_allow_html=True)
                    st.markdown(f"<img src='{row['image']}' class='glow-img' style='width:100%;'>", unsafe_allow_html=True)
                    st.markdown(f"<p class='song-title'>{row['track_name']}</p>", unsafe_allow_html=True)
                    st.write(f"**Artist:** {row['artist']}")
                    st.write(f"**Album:** {row['album']}")
                    st.write(f"**Popularity:** {row['popularity']}")
                    st.markdown(spotify_player(row["id"]), unsafe_allow_html=True)
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

            cols = st.columns(2 if st.session_state.get("is_mobile", False) else 5)
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
                    st.markdown("</div>", unsafe_allow_html=True)

        #ALBUM SEARCH
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
