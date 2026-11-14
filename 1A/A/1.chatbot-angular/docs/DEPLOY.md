# Deploy: 1.chatbot-angular

## 1. Local, no Docker

```bash
cd backend && cp .env.example .env && uv sync
uv run uvicorn app.main:app --reload --port 8000

cd ../frontend && npm install
npm start                      # http://localhost:4200 → calls http://localhost:8000 (CORS allowed by default)
```

## 2. Local, Docker Compose

```bash
cp backend/.env.example backend/.env
docker compose -f deploy/docker-compose.yaml up --build
open http://localhost:4200     # nginx in the frontend container proxies /api to backend:8000
```

## 3. Build and push images

```bash
REG=ghcr.io/<you>; TAG=$(git rev-parse --short HEAD)
docker build -t $REG/chatbot-angular-backend:$TAG backend
docker build -t $REG/chatbot-angular-frontend:$TAG frontend
docker push $REG/chatbot-angular-backend:$TAG && docker push $REG/chatbot-angular-frontend:$TAG
```

No build args needed: the frontend bundle is environment-agnostic (same-origin `/api`).

## 4. Kubernetes

```bash
kubectl apply -f deploy/k8s/00-namespace.yaml
kubectl -n chatbot-angular create secret generic backend-secrets --from-literal=GOOGLE_API_KEY=$GOOGLE_API_KEY
cd deploy/k8s
kustomize edit set image REGISTRY/chatbot-angular-backend=$REG/chatbot-angular-backend:$TAG \
                         REGISTRY/chatbot-angular-frontend=$REG/chatbot-angular-frontend:$TAG
kubectl apply -k .
kubectl -n chatbot-angular rollout status deploy/backend deploy/frontend
```

The frontend pod's nginx uses `BACKEND_URL=http://backend:80` (the backend Service). The Ingress only needs one path.

## 5. CI/CD

`.github/workflows/1-chatbot-angular.yml` runs backend lint+tests, frontend tests+build, and docker builds. Add registry push + `kubectl apply -k` / Argo CD as in `../../1.chatbot-nextjs/docs/DEPLOY.md` section 5.

## Runbook

- 502 from `/api/...`: nginx can't reach `BACKEND_URL`. `kubectl -n chatbot-angular exec deploy/frontend -- wget -qO- http://backend:80/healthz`.
- Blank page after deploy: check `try_files ... /index.html` is present (SPA fallback) and `base href="/"` in `index.html`.
- CORS errors only happen in local dev (direct calls); in Docker/k8s traffic is same-origin.
