# 6ecs — Amazon ECS Clusters

- **In plain words:** ECS is AWS's container scheduler. You describe your container (a task definition), say how many copies to keep running (a service), and ECS places them on servers (EC2) or on AWS-managed capacity (Fargate) and replaces any that die.
- Written to answer: "Have you set up an ECS cluster? Beyond min and max instances, what else did you configure?"
- Related: [5docker.md](5docker.md), [6eks.md](6eks.md), [5cloud-availability.md](5cloud-availability.md)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. The Building Blocks](#1-the-building-blocks)
- [2. Launch Types: EC2 vs Fargate](#2-launch-types-ec2-vs-fargate)
- [3. Task Definition: What You Configure](#3-task-definition-what-you-configure)
- [4. Service: What You Configure](#4-service-what-you-configure)
- [5. Scaling: Two Layers](#5-scaling-two-layers)
- [6. Deployments](#6-deployments)
- [7. Networking And Service-To-Service Calls](#7-networking-and-service-to-service-calls)
- [8. Security: Roles And Secrets](#8-security-roles-and-secrets)
- [9. Observability](#9-observability)
- [10. The Setup Checklist (Interview Answer)](#10-the-setup-checklist-interview-answer)
- [11. Failure Modes](#11-failure-modes)
- [12. Interview Questions](#12-interview-questions)
- [References](#references)

---

## 0. One-Minute Version

- **What:** a managed container orchestrator: cluster → services → tasks, with AWS running the control plane
- **Why:** keep N healthy copies of a container running, behind a load balancer, with rolling deploys and autoscaling, without running Kubernetes
- **How:** task definition (container spec) + service (desired count, LB, deploy and scaling rules) + capacity (Fargate or EC2 via capacity providers)
- **Catch:** two scaling layers on EC2 (tasks and instances) must agree; AWS-specific, so less portable than Kubernetes
- 🗣 "Service auto scaling sets how many tasks I need; the capacity provider's managed scaling makes sure there are instances to place them on, or Fargate removes that layer."

## 1. The Building Blocks

```text
Cluster
 ├─ Capacity providers: FARGATE, FARGATE_SPOT, or an EC2 Auto Scaling group
 └─ Service "orders"  (desired=6, ALB target group, rolling deploy)
      └─ Tasks (copies), each = one or more containers from Task Definition "orders:42"
```

| Piece | In plain words |
|---|---|
| Cluster | A logical group of capacity and services |
| Task definition | Versioned JSON recipe: image, CPU, memory, ports, env, roles, logging |
| Task | One running copy of a task definition (like a Kubernetes pod) |
| Service | Keeps N tasks running, replaces failures, registers them with a load balancer |
| Capacity provider | Where tasks run: Fargate, Fargate Spot, or an EC2 Auto Scaling group |
| Container agent | Runs on each EC2 instance and talks to the ECS control plane (not needed on Fargate) |

## 2. Launch Types: EC2 vs Fargate

| | Fargate | EC2 |
|---|---|---|
| Servers | None to manage; per-task microVM | You run an Auto Scaling group of instances |
| Pricing | Per task vCPU and GB per second | Per instance, whether full or not |
| Scaling layers | One: tasks | Two: tasks and instances |
| Control | Limited (no GPUs historically, no host access) | Full: instance types, GPUs, daemons, custom AMIs |
| Good at | Most web services and workers; small teams | High steady load (better bin packing, Savings Plans), GPUs, special hardware |

- Default: Fargate unless cost at steady high utilization, GPUs or host-level control decide otherwise
- Fargate Spot: up to ~70% cheaper, can be interrupted with a two-minute warning (AWS docs); good for workers, risky for the only copy of an API

## 3. Task Definition: What You Configure

- Image (pin by digest or immutable tag from ECR)
- CPU and memory at task level (Fargate requires valid combinations, e.g. 0.5 vCPU / 1 GB)
- Container-level soft and hard memory limits (EC2)
- Port mappings; network mode `awsvpc` (each task gets its own ENI and IP)
- Environment variables, and **secrets** from Secrets Manager or SSM Parameter Store
- **Task role** (what the app may call) and **execution role** (what ECS needs: pull from ECR, write logs, read secrets)
- Logging: `awslogs` driver to CloudWatch, or FireLens to other destinations
- Container health check command
- `stopTimeout` for graceful shutdown on SIGTERM
- Sidecars (log router, X-Ray or OpenTelemetry collector, Envoy) as extra containers in the same task

## 4. Service: What You Configure

| Setting | What it decides |
|---|---|
| Desired count | How many tasks run normally |
| Placement | Spread across AZs (`spread` by `attribute:ecs.availability-zone`), binpack by memory, constraints (EC2) |
| Load balancer | ALB / NLB target group, container name and port |
| Health check grace period | Time to ignore LB health checks while the app starts (JVM warm-up) |
| Deployment config | `minimumHealthyPercent`, `maximumPercent` (rolling update speed and headroom) |
| Deployment circuit breaker | Stop and roll back automatically if new tasks keep failing |
| Capacity provider strategy | Mix, e.g. base 2 on FARGATE, the rest weighted toward FARGATE_SPOT |
| Service discovery / Service Connect | How other services find this one |
| Subnets and security groups | Private subnets in 3 AZs; SG allows the ALB only |

## 5. Scaling: Two Layers

- **In plain words:** first decide how many copies of the app you need; then, on EC2, make sure there are enough servers to hold them.

1. **Service auto scaling (tasks)** via Application Auto Scaling
   - Target tracking: keep average CPU at 60%, or ALB requests per target at 500
   - Step scaling on CloudWatch alarms; scheduled scaling for known peaks
   - Min and max task counts; scale-in cooldown longer than scale-out
   - Queue workers: scale on SQS backlog per task (messages visible ÷ running tasks)
2. **Cluster capacity (EC2 only)** via an Auto Scaling group linked to a capacity provider
   - ASG min / max / desired: the instance floor and ceiling
   - **Managed scaling** with a target capacity (e.g. 90–100%): ECS adds instances when tasks can't be placed
   - **Managed termination protection** and draining: don't kill instances still running tasks
   - Instance types sized so tasks pack well (avoid a 3 GB task on 4 GB instances leaving waste)
- Fargate: only layer 1; AWS finds the capacity
- 🗣 "Min/max on the ASG is only the floor and ceiling; managed scaling on the capacity provider is what actually adds instances when tasks are pending."

## 6. Deployments

| Strategy | How | Rollback |
|---|---|---|
| Rolling (ECS default) | Start new tasks, drain old ones, within `minimumHealthyPercent` / `maximumPercent` | Circuit breaker auto-rollback, or redeploy the old revision |
| Blue/green (CodeDeploy) | Full new task set behind a second target group; shift traffic all at once, linear or canary | Shift traffic back instantly |
| External | Your own controller | Yours |

- Example: desired 6, min healthy 100%, max 200% → ECS starts 6 new tasks before stopping old ones (needs spare capacity)
- Health: ALB health check path + container health check + grace period
- Graceful shutdown: the app handles SIGTERM, stops taking requests, finishes in-flight ones within `stopTimeout`; ALB deregistration delay matches it

## 7. Networking And Service-To-Service Calls

- `awsvpc` mode: each task has its own IP and security group (required on Fargate)
- Private subnets + NAT gateway per AZ (or VPC endpoints for ECR, S3, CloudWatch, Secrets Manager to avoid NAT costs)
- Inbound: internet-facing ALB in public subnets → tasks in private subnets
- Service-to-service
  - Internal ALB
  - Cloud Map service discovery (DNS names)
  - ECS Service Connect: client-side proxy with retries, timeouts and metrics
  - App Mesh was the older option; AWS announced its end of support (check current status)

## 8. Security: Roles And Secrets

| Role | Used by | Typical permissions |
|---|---|---|
| Task execution role | The ECS agent / Fargate | Pull from ECR, write CloudWatch logs, read the secrets named in the task definition |
| Task role | Your application code | Its own DynamoDB tables, S3 prefixes, SQS queues: least privilege |
| Instance role (EC2) | The container agent on the host | Register with ECS; keep it minimal, apps use the task role |

- Secrets injected at start from Secrets Manager / SSM, never baked into the image or plain env in the task definition
- Read-only root filesystem, non-root user, ECR image scanning
- Security groups per service: allow only the callers that need it

## 9. Observability

- Logs: `awslogs` to CloudWatch Logs, or FireLens (Fluent Bit) to OpenSearch, Datadog, S3
- Metrics: service CPU and memory; Container Insights for per-task metrics; ALB target metrics (latency, 5xx, healthy hosts)
- Traces: OpenTelemetry or X-Ray sidecar
- Events: ECS service events show placement failures ("unable to place a task because no container instance met all requirements")
- Alarms: running < desired, unhealthy targets, 5xx rate, CPU / memory near limits, deployment failures

## 10. The Setup Checklist (Interview Answer)

- **In plain words:** this is the answer to "what did you configure besides min and max?"

1. **Capacity:** Fargate (or EC2 ASG + capacity provider with managed scaling and termination protection); instance types sized for packing
2. **Task definition:** CPU / memory, image by immutable tag, health check, logging, secrets, task role vs execution role, stop timeout
3. **Service:** desired count, spread across 3 AZs, ALB target group, health check grace period
4. **Service auto scaling:** min / max tasks, target tracking on CPU or requests per target (or queue depth), cooldowns
5. **Deployments:** rolling with circuit breaker auto-rollback, or blue/green via CodeDeploy; min healthy / max percent
6. **Networking:** private subnets, SGs per service, VPC endpoints or NAT per AZ, service discovery or Service Connect
7. **Observability:** logs, Container Insights, ALB alarms, running-vs-desired alarm
8. **Infra as code:** all of the above in Terraform or CDK, task definitions versioned with the app

- 🗣 "Beyond min and max, I set target-tracking scaling on requests per target, AZ spread, a health check grace period for JVM warm-up, the deployment circuit breaker, separate task and execution roles, secrets from Secrets Manager, and alarms on running versus desired tasks."

## 11. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Tasks stuck PENDING | No EC2 capacity, ENI limits, no matching instance | Service events "unable to place" | Managed scaling, bigger / more instances, Fargate |
| Deploy loop | New tasks fail health checks | Tasks start and stop repeatedly | Circuit breaker rollback; longer grace period; fix the health endpoint |
| Killed during startup | Health check grace period too short for JVM warm-up | Tasks marked unhealthy at ~30–60 s | Raise grace period; readiness endpoint |
| OOM kills | Memory limit too low; heap not sized to the container | Exit code 137 | `MaxRAMPercentage`, more memory |
| Dropped requests on deploy | No graceful shutdown; deregistration delay mismatch | 5xx spikes during deploys | Handle SIGTERM; align `stopTimeout` and deregistration delay |
| Image pull failure | Execution role lacks ECR access; no NAT or VPC endpoint | `CannotPullContainerError` | Fix role; add ECR, S3 endpoints or NAT |
| Spot interruption wipeout | All tasks on Fargate Spot | Capacity drops suddenly | Base count on on-demand FARGATE |

## 12. Interview Questions

**Q1. ECS on EC2 or Fargate?**
- L4: Fargate removes server management and the second scaling layer; EC2 gives control and can be cheaper at steady high load
- L5 extra: the deciding variables are utilization (bin packing pays only when instances stay full), special hardware (GPUs), and team size; a mixed strategy with a Fargate base and Spot overflow is common

**Q2. How does ECS autoscaling work?**
- L4: Application Auto Scaling changes the service's desired count from CloudWatch metrics (target tracking or steps)
- L5 extra: on EC2, the capacity provider's managed scaling grows the ASG when tasks can't be placed; scale-in must drain tasks first (managed termination protection)

**Q3. Task role vs execution role?**
- L4: execution role is for ECS to pull images, write logs and fetch secrets; task role is for the app's own AWS calls
- L5 extra: separating them means a compromised app can't read other services' secrets or pull arbitrary images; scope the task role to exact resource ARNs

## References

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [ECS capacity providers and managed scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/asg-capacity-providers.html)
- [ECS service auto scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html)
- [ECS deployment circuit breaker](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html)
