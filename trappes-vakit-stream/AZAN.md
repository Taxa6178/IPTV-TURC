AZAN.md

How to add an Azan (call to prayer) audio to the HLS stream

1) Place your azan MP3 file at: trappes-vakit-stream/public/azan.mp3
   - The filename must be exactly "azan.mp3".
   - Use an MP3 audio snippet that you have rights to use.

2) The streamer will automatically detect the file and play it when a prayer time is reached.
   - The script checks Aladhan timings for Trappes and will play the audio when the current time is within -10s..+120s of a prayer.
   - The azan is mixed into the HLS stream by restarting ffmpeg with the azan MP3 as a second input.

3) Important notes and caveats
   - The server's timezone should match the target timezone (Trappes). If your server runs in UTC, prayer times may be offset. For best results run the container on a server with Europe/Paris timezone or modify the code to use a timezone-aware parsing.
   - If no azan.mp3 is present, the stream will continue without audio.
   - Make sure your azan audio length is reasonable (e.g., 30-90s). The script uses "-shortest" so the stream will include the audio length.

4) Troubleshooting
   - If ffmpeg doesn't include audio, check container logs (docker logs -f trappes-vakit) for ffmpeg errors.
   - Ensure the azan file is readable by the container and not corrupted.

