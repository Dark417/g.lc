# --- build ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- runtime: nginx serves static files + proxies /api, unprivileged port 8080 ---
FROM nginxinc/nginx-unprivileged:alpine
# nginx's entrypoint runs envsubst on /etc/nginx/templates/*.template -> /etc/nginx/conf.d/
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
ENV BACKEND_URL=http://backend:8000
EXPOSE 8080
