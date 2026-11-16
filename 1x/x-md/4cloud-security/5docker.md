# 5docker — Containers, Images, Registries (Light)

- **In plain words:** a container is your app packed with everything it needs into one sealed box (an image), so it runs the same on a laptop, in CI and in the cloud. A registry is the warehouse where the boxes are stored.
- A light completeness file: the vocabulary and the decisions, not a tutorial
- Next: running containers at scale in [6ecs.md](6ecs.md) and [6eks.md](6eks.md)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. The Pieces](#1-the-pieces)
- [2. Image Building](#2-image-building)
- [3. Registries](#3-registries)
- [4. Running Containers](#4-running-containers)
- [5. Container vs VM vs Serverless](#5-container-vs-vm-vs-serverless)
- [6. Best Practices](#6-best-practices)
- [7. Interview Questions](#7-interview-questions)
- [References](#references)

---

## 0. One-Minute Version

- **What:** OS-level isolation (Linux namespaces + cgroups) sharing the host kernel, packaged as layered images
- **Why:** same artifact everywhere; fast start; dense packing on hosts
- **How:** `Dockerfile` → `docker build` → image → push to a registry → an orchestrator pulls and runs it
- **Catch:** shared kernel means weaker isolation than a VM; images bloat and carry vulnerabilities if unmanaged
- 🗣 "The image is the deployable unit: built once in CI, scanned, tagged immutably, pushed to ECR, and promoted unchanged through environments."

## 1. The Pieces

| Term | In plain words |
|---|---|
| Image | Read-only template: layers of files plus metadata (entrypoint, env, ports) |
| Layer | One filesystem change from one `Dockerfile` step; cached and shared between images |
| Container | A running instance of an image, with a thin writable layer on top |
| Dockerfile | The recipe for building an image |
| Registry | Server that stores and serves images (ECR, Docker Hub, GHCR, Artifact Registry) |
| Repository | One image name inside a registry, holding many tags |
| Tag | Human label for an image version (`1.4.2`, `latest`); can be moved |
| Digest | Content hash (`sha256:…`); immutable, the safest way to pin |
| Namespaces / cgroups | Kernel features: namespaces isolate what a process sees; cgroups limit CPU and memory |
| OCI | Open Container Initiative: the standard image and runtime formats Docker, containerd and others follow |
| Runtime | What actually runs containers: containerd, runc (Docker Engine uses them under the hood) |

## 2. Image Building

```dockerfile
# Multi-stage build: compile in a big image, ship a small one
FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
COPY . .
RUN ./mvnw -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /src/target/app.jar app.jar
USER 10001                                  # not root
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
```

- Multi-stage builds keep compilers out of the runtime image
- Order steps from least to most often changing, so cached layers survive (dependencies before source)
- `.dockerignore` keeps `.git`, `target/`, secrets out of the build context
- Smaller bases: `-jre`, distroless, or Alpine (watch musl libc differences)
- Java in containers: the JVM reads cgroup limits; set heap with `MaxRAMPercentage`, not a fixed `-Xmx` that ignores the limit

## 3. Registries

| Registry | Where | Notes |
|---|---|---|
| Amazon ECR | AWS | IAM auth, scan on push, lifecycle policies, cross-region replication, immutable tags option |
| Google Artifact Registry | GCP | Also stores Maven, npm, Python packages |
| Azure Container Registry | Azure | Geo-replication |
| OCI Container Registry (OCIR) | Oracle Cloud | Per-region |
| Docker Hub | Public SaaS | Pull rate limits for anonymous users |
| GitHub Container Registry | GitHub | Tied to repos and Actions |
| Harbor / JFrog Artifactory / Nexus | Self-hosted | Artifactory and Nexus also store jars, npm, PyPI ("artifact repository") |

- Artifact repository vs container registry: an artifact repository stores all build outputs (jars, wheels, npm, Helm charts, images); a container registry stores images only
- Tag strategy: immutable version or git SHA tags; never deploy `latest` to production
- Lifecycle policy: expire untagged and old images to control cost
- Pull access: ECS and EKS pull from ECR with an IAM role (task execution role or node role)

## 4. Running Containers

| Command / concept | What it does |
|---|---|
| `docker run -p 8080:8080 -e KEY=v --memory 512m img` | Run with port mapping, env and a memory limit |
| Volumes / bind mounts | Persist data outside the container's writable layer |
| Networks | Bridge network on one host; containers reach each other by name |
| `docker compose` | Run several containers together locally (app + Postgres + Redis) |
| Health check | `HEALTHCHECK` in the image, or the orchestrator's probe |
| Logs | Write to stdout / stderr; the platform collects them |

- Containers are cattle: no state inside, config from env, logs to stdout (12-factor app)

## 5. Container vs VM vs Serverless

| Option | Isolation | Start time | Good at | Bad at |
|---|---|---|---|---|
| VM (EC2) | Own kernel, hypervisor | Tens of seconds to minutes | Strong isolation, any OS | Heavier, slower to scale |
| Container (ECS, EKS) | Shared kernel, namespaces | Seconds | Density, portability, steady services | Weaker isolation; you manage the cluster (less so on Fargate) |
| microVM (Firecracker: Lambda, Fargate) | Lightweight VM per task | Sub-second to seconds | VM isolation with container speed | Managed only |
| Function (Lambda) | microVM per function | Milliseconds warm, cold starts slower | Spiky, event-driven work | Time limits, cold starts, per-request cost at high volume |

## 6. Best Practices

- Build once, promote the same digest through dev, staging, prod → prevents "works in staging" drift
- Run as non-root, read-only root filesystem where possible → limits damage from a compromise
- Scan images (ECR scan, Trivy) and rebuild on base-image patches → prevents known CVEs shipping
- No secrets in images or layers; inject at runtime (Secrets Manager, env from the orchestrator) → layers are readable by anyone who can pull
- Set CPU and memory limits → prevents one container starving the host
- Graceful shutdown on SIGTERM → prevents dropped requests during deploys

## 7. Interview Questions

**Q1. Container vs VM?**
- L4: containers share the host kernel and isolate with namespaces and cgroups; VMs run their own kernel on a hypervisor
- L5 extra: Firecracker microVMs (Lambda, Fargate) give VM-level isolation with near-container start times, which is why multi-tenant serverless uses them

**Q2. How do you keep images small and secure?**
- L4: multi-stage builds, slim bases, `.dockerignore`, non-root user
- L5 extra: pin by digest, scan in CI and on push, immutable tags, rebuild on base-image CVEs, no secrets in layers

## References

- [Docker docs — Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Amazon ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- [Open Container Initiative specifications](https://opencontainers.org/)
