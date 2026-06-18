const fs = require('fs');
const { spawn } = require('child_process');
const express = require('express');
const puppeteer = require('puppeteer');

const GITHUB_PAGE = 'https://taxa6178.github.io/IPTV-TURC/trappes-vakit/index.html';
const OUT_DIR = 'public/live';
const OUT_IMG = `${OUT_DIR}/current.png`;
const HLS_PLAYLIST = `${OUT_DIR}/trappes.m3u8`;

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

let ffmpegProc = null;

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

function startFfmpeg() {
  // Clean previous HLS files
  try { fs.readdirSync(OUT_DIR).forEach(f => { if (f.startsWith('trappes')) fs.unlinkSync(`${OUT_DIR}/${f}`); }); } catch(e){}

  const args = [
    '-y',
    '-loop', '1',
    '-framerate', '2',
    '-i', OUT_IMG,
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
    '-hls_time', '4',
    '-hls_list_size', '6',
    '-hls_flags', 'delete_segments+append_list',
    '-hls_segment_filename', `${OUT_DIR}/trappes_%03d.ts`,
    `${OUT_DIR}/trappes.m3u8`
  ];

  console.log('Starting ffmpeg with args:', args.join(' '));
  ffmpegProc = spawn('ffmpeg', args, { stdio: ['ignore','inherit','inherit'] });
  ffmpegProc.on('exit', (code, sig) => {
    console.log('ffmpeg exited', code, sig);
    ffmpegProc = null;
  });
}

async function updateLoop() {
  while (true) {
    try {
      console.log('Taking screenshot...');
      await takeScreenshot();
      console.log('Screenshot saved:', OUT_IMG);
      if (ffmpegProc) {
        console.log('Killing previous ffmpeg to reload image...');
        ffmpegProc.kill('SIGTERM');
        // wait a bit for process to exit
        await new Promise(r => setTimeout(r, 1200));
      }
      startFfmpeg();
    } catch (e) {
      console.error('Update loop error:', e);
    }
    // wait 60s before next screenshot
    await new Promise(r => setTimeout(r, 60*1000));
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
