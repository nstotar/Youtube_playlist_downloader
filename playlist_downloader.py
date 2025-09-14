import os
from pytubefix import YouTube, Playlist
import ipywidgets as widgets
from IPython.display import display

# Define save location
save_path = os.path.join(os.getcwd(), "downloads")
os.makedirs(save_path, exist_ok=True)

print("📂 Downloads will be saved inside:", save_path)  # Create folder if not exists

link_input = widgets.Text(
    value='',
    placeholder='Paste YouTube video or playlist link here',
    description='Link:',
    disabled=False
)

download_button = widgets.Button(
    description='Download',
    button_style='success',
    tooltip='Click to download video/playlist',
    icon='⬇️'
)

output = widgets.Output()


def normalize_link(link: str) -> str:
    if "youtu.be" in link:
        video_id = link.split("/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return link

# Download function
def download_video(b):
    output.clear_output()
    with output:
        link = normalize_link(link_input.value.strip())
        if not link:
            print("❌ Please enter a valid YouTube link")
            return
        try:
            if "playlist" in link.lower():
                # Playlist download
                p = Playlist(link)
                total_videos = len(p.videos)
                print(f"📂 Downloading Playlist: {p.title} ({total_videos} videos)")
                
                for idx, video in enumerate(p.videos, start=1):
                    print(f"🎬 ({idx}/{total_videos}) {video.title}")
                    stream = video.streams.filter(progressive=True, file_extension="mp4") \
                                          .order_by("resolution") \
                                          .desc() \
                                          .first()
                    stream.download(output_path=desktop)
                print(f"✅ Playlist download completed! Saved to: {desktop}")
            else:
                # Single video download
                yt = YouTube(link)
                print(f"🎬 Downloading: {yt.title}")
                stream = yt.streams.filter(progressive=True, file_extension="mp4") \
                                   .order_by("resolution") \
                                   .desc() \
                                   .first()
                stream.download(output_path=desktop)
                print(f"✅ Video download completed! Saved to: {desktop}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

download_button.on_click(download_video)

display(link_input, download_button, output)
