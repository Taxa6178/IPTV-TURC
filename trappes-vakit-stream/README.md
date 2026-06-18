# Trappes Vakit HLS stream

This directory contains a small Dockerized service that periodically captures the GitHub Pages prayer-times page and converts it into a simple HLS stream (for OTT Navigator / IPTV players).

How it works
- A Node.js script (app.js) uses Puppeteer to screenshot the page at https://taxa6178.github.io/IPTV-TURC/trappes-vakit/index.html every 60 seconds.
- After each screenshot the script (re)starts ffmpeg which loops the screenshot into a short HLS stream served from /live/trappes.m3u8.
- An Express static server serves the HLS files on port 8080.

Build & run (example)

1) Build the Docker image:

   docker build -t trappes-vakit-stream ./trappes-vakit-stream

2) Run the container (map port 8080):

   docker run -d --name trappes-vakit -p 8080:8080 trappes-vakit-stream

3) In your IPTV playlist use the HLS URL (replace HOST with your server IP or domain):

   http://HOST:8080/live/trappes.m3u8

Notes & caveats
- This is a lightweight approach for displaying a visual "slide" in IPTV players. It is not a low-latency live video and ffmpeg is restarted every minute (when a new screenshot is taken) so segment continuity is best-effort.
- Make sure your server has enough CPU and bandwidth. Puppeteer/Chromium + ffmpeg can be CPU intensive.
- If you deploy to a public server, secure it (firewall, TLS, reverse proxy).
- If you prefer a different rendering approach (direct HTML->video, animated overlay, audio azan), I can help extend this service.
