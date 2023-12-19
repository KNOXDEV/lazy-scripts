# name: Download YouTube as Audio
# desktop: true
# query: "Enter YouTube URL:"
yt-dlp -o "~/Downloads/%(title)s.%(ext)s" --restrict-filenames -f ba --remux-video ogg "$1"