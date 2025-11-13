import streamlit as st
import os
from pytube import YouTube, Playlist
from pydub import AudioSegment

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

st.title("YouTube Video & Audio Downloader")
st.info(f"📂 Downloads will be saved in: `{DOWNLOAD_DIR}`")

link = st.text_input("Paste YouTube video or playlist link", "")

download_type = st.selectbox(
    "Select download type",
    ("Video - mp4", "Audio - mp3")
)

video_resolution = st.selectbox(
    "Select video resolution",
    ("360p", "480p", "720p", "1080p", "1440p")  # 1440p = 2k
)

def normalize_link(link: str) -> str:
    if "youtu.be" in link:
        video_id = link.split("/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return link

def download_mp3(yt, output_dir):
    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    if not audio_stream:
        return False, "No audio stream found."
    temp_path = audio_stream.download(output_path=output_dir)
    base, _ = os.path.splitext(temp_path)
    mp3_path = base + ".mp3"
    try:
        audio = AudioSegment.from_file(temp_path)
        audio.export(mp3_path, format="mp3")
        os.remove(temp_path)
        return True, mp3_path
    except Exception as e:
        return False, str(e)

def download_video(yt, resolution, output_dir):
    stream = yt.streams.filter(progressive=True, file_extension="mp4", res=resolution).first()
    if not stream:
        return False, f"No mp4 stream available at {resolution}."
    video_path = stream.download(output_path=output_dir)
    return True, video_path

if st.button("⬇️ Download"):
    link = normalize_link(link.strip())
    if not link:
        st.error("❌ Please enter a valid YouTube link")
    else:
        try:
            if "playlist" in link.lower():
                p = Playlist(link)
                total_videos = len(p.video_urls)
                st.write(f"📂 Downloading Playlist: `{p.title}` ({total_videos} videos)")
                progress_bar = st.progress(0)
                for idx, video_url in enumerate(p.video_urls, start=1):
                    yt = YouTube(video_url)
                    st.write(f"🎬 ({idx}/{total_videos}) {yt.title}")
                    if download_type == "Audio - mp3":
                        success, info = download_mp3(yt, DOWNLOAD_DIR)
                        if success:
                            st.success(f"✅ Downloaded MP3: {yt.title}")
                        else:
                            st.warning(f"⚠️ {info}")
                    else:  # Video download
                        res = video_resolution
                        success, info = download_video(yt, res, DOWNLOAD_DIR)
                        if success:
                            st.success(f"✅ Downloaded {res} MP4: {yt.title}")
                        else:
                            st.warning(f"⚠️ {info}")
                    progress_bar.progress(idx / total_videos)
                st.success(f"✅ Playlist download completed! Saved to: `{DOWNLOAD_DIR}`")
            else:
                yt = YouTube(link)
                st.write(f"🎬 Downloading: `{yt.title}`")
                if download_type == "Audio - mp3":
                    success, info = download_mp3(yt, DOWNLOAD_DIR)
                    if success:
                        st.success(f"✅ Downloaded MP3: {yt.title}")
                    else:
                        st.warning(f"⚠️ {info}")
                else:
                    res = video_resolution
                    success, info = download_video(yt, res, DOWNLOAD_DIR)
                    if success:
                        st.success(f"✅ Downloaded {res} MP4: {yt.title}")
                    else:
                        st.warning(f"⚠️ {info}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

st.caption("For MP3 downloads, ffmpeg must be installed. Only public videos are supported. Playlist downloads may take time.")
