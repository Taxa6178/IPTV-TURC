const fs = require('fs');
const { spawn } = require('child_process');
const express = require('express');
const puppeteer = require('puppeteer');

const GITHUB_PAGE = 'https://taxa6178.github.io/IPTV-TURC/trappes-vakit/index.html';
const OUT_DIR = 'public/live';
const OUT_IMG = `${OUT_DIR}/current.png`;
const HLS_PLAYLIST = `${OUT_DIR}/trappes.m3u8`;
const AZAN_FILE = 'public/azan.mp3'; // place your azan MP3 here

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

let ffmpegProc = null;
let lastPlayed = {}; // { 'YYYY-MM-DD': {Fajr: true, Dhuhr: true, ...} }

async function takeScreenshot() {
  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    await page.goto(GITHUB_PAGE, { waitUntil: 'networkidle2', timeout: 30000 });
    await page.screenshot({ path: OUT_IMG, fullPage: false });
  } catch (e) {
    console.error('Screenshot error:', e);
  } finally {
    await browser.close();
  }
}

function startFfmpeg(withAzan = false) {
  // Clean previous HLS files
  try { fs.readdirSync(OUT_DIR).forEach(f => { if (f.startsWith('trappes')) fs.unlinkSync(`${OUT_DIR}/${f}`); }); } catch(e){}

  const args = [
    '-y',
    '-loop', '1',
    '-framerate', '2',
    '-i', OUT_IMG,
  ];

  if (withAzan && fs.existsSync(AZAN_FILE)) {
    // add audio input
    args.push('-i', AZAN_FILE);
    // video codec
    args.push(
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-preset', 'veryfast',
      '-tune', 'stillimage',
      '-r', '25',
      '-g', '50',
      '-keyint_min', '50',
      '-b:v', '800k',
      '-maxrate', '856k',
      '-bufsize', '1200k',
      // audio mapping and encoding
      '-c:a', 'aac',
      '-b:a', '128k',
      '-map', '0:v',
      '-map', '1:a',
      '-shortest'
    );
  } else {
    args.push(
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-preset', 'veryfast',
      '-tune', 'stillimage',
      '-r', '25',
      '-g', '50',
      '-keyint_min', '50',
      '-b:v', '800k',
      '-maxrate', '856k',
      '-bufsize', '1200k'
    );
  }

  args.push(
    '-hls_time', '4',
    '-hls_list_size', '6',
    '-hls_flags', 'delete_segments+append_list',
    '-hls_segment_filename', `${OUT_DIR}/trappes_%03d.ts`,
    `${OUT_DIR}/trappes.m3u8`
  );

  console.log('Starting ffmpeg with args:', args.join(' '));
  ffmpegProc = spawn('ffmpeg', args, { stdio: ['ignore','inherit','inherit'] });
  ffmpegProc.on('exit', (code, sig) => {
    console.log('ffmpeg exited', code, sig);
    ffmpegProc = null;
  });
}

function parseTimeToDate(timeStr, dateObj) {
  // timeStr like "05:12" or "05:12 (CEST)" sometimes includes timezone; strip non-digit and colon
  const match = timeStr.match(/(\d{1,2}:\d{2})/);
  if (!match) return null;
  const [hh, mm] = match[1].split(':').map(Number);
  return new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate(), hh, mm, 0);
}

async function fetchTimings() {
  try {
    const city = 'Trappes';
    const country = 'France';
    const res = await fetch(`https://api.aladhan.com/v1/timingsByCity?city=${encodeURIComponent(city)}&country=${encodeURIComponent(country)}&method=2`);
    const data = await res.json();
    if (data.code !== 200) throw new Error('API hata');
    return data.data.timings; // object with Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha
  } catch (e) {
    console.error('fetchTimings error', e);
    return null;
  }
}

let lastDateKey = null;

async function updateLoop() {
  while (true) {
    try {
      console.log('Taking screenshot...');
      await takeScreenshot();
      console.log('Screenshot saved:', OUT_IMG);

      // Fetch timings and decide whether to play azan
      const timings = await fetchTimings();
      const now = new Date();
      const dateKey = `${now.getFullYear()}-${now.getMonth()+1}-${now.getDate()}`;
      if (dateKey !== lastDateKey) {
        // reset played flags for new day
        lastPlayed[dateKey] = {};
        lastDateKey = dateKey;
      }

      let shouldPlayAzan = false;
      if (timings) {
        // check prayer keys where we want azan: Fajr, Dhuhr, Asr, Maghrib, Isha
        const keys = ['Fajr','Dhuhr','Asr','Maghrib','Isha'];
        for (const k of keys) {
          const timeStr = timings[k];
          const prayerDate = parseTimeToDate(timeStr, now);
          if (!prayerDate) continue;
          const diffSec = (prayerDate - now) / 1000;
          // play azan if we're within [-10s, +120s] of the scheduled time
          if (diffSec <= 120 && diffSec >= -10) {
            if (!lastPlayed[dateKey][k]) {
              console.log(`Prayer ${k} is due (diff ${diffSec}s). Will play azan.`);
              shouldPlayAzan = true;
              lastPlayed[dateKey][k] = true; // mark as played for today
            } else {
              console.log(`Prayer ${k} is due but already played today.`);
            }
            break; // only play one azan at a time
          }
        }
      }

      if (ffmpegProc) {
        console.log('Killing previous ffmpeg to reload image/audio...');
        ffmpegProc.kill('SIGTERM');
        await new Promise(r => setTimeout(r, 1200));
      }
      startFfmpeg(shouldPlayAzan);

    } catch (e) {
      console.error('Update loop error:', e);
    }
    // wait 30s before next cycle (we want higher resolution around prayer times)
    await new Promise(r => setTimeout(r, 30*1000));
  }
}

// Start static server to serve HLS
const app = express();
app.use('/live', express.static(`${__dirname}/public/live`));
app.get('/', (req, res) => res.send('Trappes Vakit Stream - HLS server.')); 
const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`HTTP server listening on http://0.0.0.0:${port}/`));

// ensure out dir exists
if (!fs.existsSync('public')) fs.mkdirSync('public');
if (!fs.existsSync('public/live')) fs.mkdirSync('public/live');

// start the loop
updateLoop().catch(e => console.error(e));
