# --- build ---
FROM node:22-alpine AS build
WORKDIR /app
# npm 10.9 crashes resolving jsdom's optional `canvas` peer; npm 11 is fixed.
RUN npm install -g npm@11
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- runtime: nginx serves static files + proxies /api on unprivileged port 8080 ---
FROM nginxinc/nginx-unprivileged:alpine
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
ENV BACKEND_URL=http://backend:8000
EXPOSE 8080
