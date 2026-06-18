# Trappes Vakit HLS stream

This directory contains a small Dockerized service that periodically captures the GitHub Pages prayer-times page and converts it into a simple HLS stream (for OTT Navigator / IPTV players).

How it works
- A Node.js script (app.js) uses Puppeteer to screenshot the page at https://taxa6178.github.io/IPTV-TURC/trappes-vakit/index.html every 30–60 seconds.
- After each screenshot the script (re)starts ffmpeg which loops the screenshot into a short HLS stream served from /live/trappes.m3u8.
- If you place an azan audio file at trappes-vakit-stream/public/azan.mp3 the service will detect prayer times (via Aladhan API) and play the azan audio automatically around each prayer time.

Build & run (example)

1) Build the Docker image:

   docker build -t trappes-vakit-stream ./trappes-vakit-stream

2) Run the container (map port 8080):

   docker run -d --name trappes-vakit -p 8080:8080 trappes-vakit-stream

3) In your IPTV playlist use the HLS URL (replace HOST with your server IP or domain):

   http://HOST:8080/live/trappes.m3u8

Adding Azan audio
- Place your MP3 at trappes-vakit-stream/public/azan.mp3. See AZAN.md for details.

Notes & caveats
- This is a lightweight approach for displaying a visual "slide" in IPTV players. It is not a low-latency live video and ffmpeg is restarted whenever a new screenshot or azan event occurs, so segment continuity is best-effort.
- Make sure your server has enough CPU and bandwidth. Puppeteer/Chromium + ffmpeg can be CPU intensive.
- If you deploy to a public server, secure it (firewall, TLS, reverse proxy).
- If you prefer a different rendering approach (direct HTML->video, animated overlay, or advanced audio scheduling), I can help extend this service.
