# name: Download YouTube Video
# desktop: true
# query: "Enter YouTube URL:"
yt-dlp -o "~/Downloads/%(title)s.%(ext)s" --restrict-filenames --remux-video mp4 "$1"