import streamlit as st
import os
from pytube import YouTube, Playlist

# DEFAULT DOWNLOAD PATH (within app folder)
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

st.title("YouTube Video & Playlist Downloader")
st.info(f"📂 Downloads will be saved in: `{DOWNLOAD_DIR}`")

link = st.text_input("Paste YouTube video or playlist link", "")

def normalize_link(link: str) -> str:
    if "youtu.be" in link:
        video_id = link.split("/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return link

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
                    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
                    if stream:
                        stream.download(output_path=DOWNLOAD_DIR)
                    else:
                        st.warning(f"⚠️ No suitable MP4 stream for {yt.title}")
                    progress_bar.progress(idx / total_videos)
                st.success(f"✅ Playlist download completed! Saved to: `{DOWNLOAD_DIR}`")
            else:
                yt = YouTube(link)
                st.write(f"🎬 Downloading: `{yt.title}`")
                stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
                if stream:
                    stream.download(output_path=DOWNLOAD_DIR)
                    st.success(f"✅ Video download completed! Saved to: `{DOWNLOAD_DIR}`")
                else:
                    st.warning("⚠️ No suitable MP4 stream found for this video.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

st.caption("Only public videos and playlists are supported. Large playlists may take time.")
