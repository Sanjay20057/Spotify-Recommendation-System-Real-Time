# 🎧 Spotify Clone — Streamlit Web App

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=for-the-badge&logo=streamlit)
![Spotify API](https://img.shields.io/badge/Spotify-Web%20API-1DB954?style=for-the-badge&logo=spotify)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A full-featured Spotify-inspired music web app built with Streamlit. Search songs, artists, and albums. Like tracks, build playlists, manage your profile — all powered by the Spotify Web API.**

[Features](#-features) · [Screenshots](#-screenshots) · [Installation](#-installation) · [Configuration](#-configuration) · [Usage](#-usage) · [Project Structure](#-project-structure)

</div>

---

## ✨ Features

### 🔐 Authentication
- Secure **Sign Up / Login** with SHA-256 hashed passwords
- **Persistent login** via encrypted cookies (stays logged in for 24 hours across sessions)
- Favorite singer field used for account recovery
- Full **account deletion** with password confirmation

### 🎵 Music Search
- Search by **Song**, **Artist**, or **Album** using a filter dropdown
- Smart artist matching — exact name → starts with → contains → highest popularity fallback
- Embedded **Spotify track players** (80px iframe) directly in the UI
- Album view with expandable track list (show more / show less)
- Top 10 similar song recommendations for every search

### ❤️ Liked Songs
- Like / Unlike any track with a single click
- Dedicated **Liked Songs** page showing all saved tracks with embedded players
- Multi-select bulk remove from liked songs

### 🎶 Playlists
- Create unlimited named playlists
- Add songs to any existing playlist directly from search results
- Visual playlist cards with neon green gradient design
- Open a playlist to view and play all tracks
- Multi-select bulk remove songs from a playlist
- Delete entire playlists in one click

### 👤 User Profile
- Upload a custom profile picture (PNG / JPG)
- Set a display name and bio
- Profile image shown in the sidebar with a live online status dot
- Remove profile picture option
- Account information panel

### 🎨 UI / Design
- **Neon green cyberpunk** aesthetic on a pure black background
- Custom background image on the login page
- Animated GIF background support for the main app
- Glowing image cards, pulsing borders, neon input fields
- Fully **mobile responsive** — columns stack on small screens, buttons go full-width
- Custom scrollbar, hover animations, and CSS transitions throughout

---

## 🖼️ Screenshots

> _Add screenshots of your app here._

| Login Page | Search Page | Playlists |
|---|---|---|
| ![login](screenshots/login.png) | ![search](screenshots/search.png) | ![playlists](screenshots/playlists.png) |

---

## 📂 Project Structure

```
spotify-clone/
│
├── app.py                        # Main Streamlit application
│
├── users.db                      # SQLite database (auto-created on first run)
│
├── Login_Background.jpeg         # Background image for the login screen
├── background.gif                # (Optional) Animated GIF for main app background
│
├── WhatsApp Image (...).jpg      # App logo shown in the top-left
│
├── requirements.txt              # Python dependencies
└── .streamlit/
    └── secrets.toml              # Spotify API credentials (CLIENT_ID, CLIENT_SECRET)
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9 or higher
- A [Spotify Developer account](https://developer.spotify.com/dashboard) (free)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/spotify-clone.git
cd spotify-clone
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration

### Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **Create App**
3. Copy your **Client ID** and **Client Secret**

Create the file `.streamlit/secrets.toml`:

```toml
CLIENT_ID = "your_spotify_client_id_here"
CLIENT_SECRET = "your_spotify_client_secret_here"
```

### Required Local Files

Make sure these files exist in the project root before running:

| File | Purpose |
|---|---|
| `Login_Background.jpeg` | Background image on the login screen |
| `background.gif` | *(Optional)* Animated background for the main app |
| Your logo `.jpg` | App logo shown top-left (update the filename in `app.py`) |

---

## 🚀 Usage

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### First Time Setup
1. Click **Sign Up** and create an account (username, password, favorite singer)
2. Log in — your session is saved in an encrypted cookie for 24 hours
3. Use the sidebar menu to navigate: **Search Music**, **Liked Songs**, **Playlists**, **Profile**

---

## 🗄️ Database Schema

The app uses a local SQLite database (`users.db`) with four tables:

| Table | Columns | Purpose |
|---|---|---|
| `users` | id, username, password, fav_singer | User accounts |
| `liked_songs` | id, username, track_id, track_name, artist, image | Per-user liked tracks |
| `playlists` | id, username, playlist_name, track_id, track_name, artist, image | Per-user playlists |
| `user_profile` | username, full_name, bio, image | Profile data and avatar |

---

## 📦 Dependencies

```
streamlit
spotipy
pandas
streamlit-cookies-manager
```

Install all at once:

```bash
pip install streamlit spotipy pandas streamlit-cookies-manager
```

---

## ⚠️ Notes

- **Playback is preview only** unless the user is logged into Spotify Premium in their browser (Spotify's embedded player limitation).
- The cookie encryption password in `app.py` (`supersecretpassword123!`) should be changed to a strong secret before deploying publicly.
- `users.db` is created automatically on first run — no manual setup needed.
- This project uses the **Spotify Client Credentials flow**, which means it can search and retrieve public data but cannot control playback or access user Spotify accounts.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

*Built with ❤️ using Streamlit + Spotify Web API*

</div>
