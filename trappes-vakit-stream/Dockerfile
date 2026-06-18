FROM node:18-bullseye

# Install ffmpeg and necessary libs for Puppeteer/Chromium
RUN apt-get update && apt-get install -y \
  ffmpeg \
  ca-certificates \
  fonts-dejavu-core \
  libnss3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libx11-xcb1 \
  libxcomposite1 \
  libxrandr2 \
  libasound2 \
  libgbm1 \
  libxshmfence1 \
  wget \
  --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json .
RUN npm install --unsafe-perm

COPY . .

EXPOSE 8080
CMD ["node","app.js"]
