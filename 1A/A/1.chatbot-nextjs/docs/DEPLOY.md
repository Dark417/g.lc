# Deploy: 1.chatbot-nextjs

## 1. Local, no Docker

```bash
# backend
cd backend
cp .env.example .env            # set GOOGLE_API_KEY
uv sync
uv run uvicorn app.main:app --reload --port 8000
# optional: ADK's debug UI for the same agent
uv run adk web app               # http://localhost:8000 in a second terminal on another port

# frontend
cd ../frontend
cp .env.example .env.local
npm install
npm run dev                     # http://localhost:3000
```

## 2. Local, Docker Compose

```bash
cp backend/.env.example backend/.env    # set GOOGLE_API_KEY
docker compose -f deploy/docker-compose.yaml up --build
```

## 3. Build and push images

```bash
REG=ghcr.io/<you>
TAG=$(git rev-parse --short HEAD)
docker build -t $REG/chatbot-nextjs-backend:$TAG backend
docker build -t $REG/chatbot-nextjs-frontend:$TAG \
  --build-arg NEXT_PUBLIC_API_URL=https://chatbot.example.com frontend
docker push $REG/chatbot-nextjs-backend:$TAG
docker push $REG/chatbot-nextjs-frontend:$TAG
```

`NEXT_PUBLIC_API_URL` is baked in at build time. With the Ingress below the browser calls `https://chatbot.example.com/api/...`, so set it to the public host.

## 4. Kubernetes

```bash
kubectl apply -f deploy/k8s/00-namespace.yaml
kubectl -n chatbot-nextjs create secret generic backend-secrets --from-literal=GOOGLE_API_KEY=$GOOGLE_API_KEY
cd deploy/k8s
kustomize edit set image REGISTRY/chatbot-nextjs-backend=$REG/chatbot-nextjs-backend:$TAG \
                         REGISTRY/chatbot-nextjs-frontend=$REG/chatbot-nextjs-frontend:$TAG
kubectl apply -k .
kubectl -n chatbot-nextjs rollout status deploy/backend deploy/frontend
```

Edit `40-ingress.yaml` host and `10-backend-config.yaml` `CORS_ORIGINS` for your domain. Delete the placeholder `Secret` block from `10-backend-config.yaml` once you manage secrets out-of-band.

## 5. CI/CD

`.github/workflows/1-chatbot-nextjs.yml` already runs lint, tests, and image builds on every PR touching this project. To deploy:

1. Add `docker/login-action` + `docker/build-push-action` in the `images` job, tag with `${{ github.sha }}`.
2. Add a `deploy` job (on `main` only) that runs the kustomize commands above with a kubeconfig from secrets, or lets Argo CD / Flux watch the kustomization.

Prefer GitOps (Argo/Flux) over `kubectl` from CI once there is more than one environment.

## Runbook

- Backend 500 on chat: check `GOOGLE_API_KEY` secret and model name. `kubectl logs deploy/backend`.
- CORS error in browser: `CORS_ORIGINS` must include the exact origin (scheme + host + port).
- Conversation "forgets" after a redeploy: expected with in-memory sessions.
