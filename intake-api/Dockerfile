# Coolify/Hetzner build for the intake API. Render's node runtime ignores this file.
# No package.json here on purpose: server.js uses only Node built-ins, so Nixpacks
# has nothing to detect and a plain image is the honest description.
FROM node:22-alpine
WORKDIR /app
COPY server.js ./
ENV NODE_ENV=production PORT=3000
EXPOSE 3000
CMD ["node", "server.js"]
