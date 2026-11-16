# 6eks — Amazon EKS And Kubernetes Essentials

- **In plain words:** Kubernetes is an open-source system that keeps your containers running the way you described them in YAML; EKS is AWS running the Kubernetes "brain" for you while your containers run on nodes you provide or on Fargate.
- Light-to-medium depth: what to know to discuss and configure it, not to run a platform team
- Related: [6ecs.md](6ecs.md) (simpler AWS-only option), [5docker.md](5docker.md), [5cloud-availability.md](5cloud-availability.md)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. Architecture](#1-architecture)
- [2. Core Objects](#2-core-objects)
- [3. Compute Options On EKS](#3-compute-options-on-eks)
- [4. Scaling: Pods And Nodes](#4-scaling-pods-and-nodes)
- [5. Networking](#5-networking)
- [6. Security](#6-security)
- [7. Deployments And Config](#7-deployments-and-config)
- [8. Observability](#8-observability)
- [9. ECS vs EKS](#9-ecs-vs-eks)
- [10. Setup Checklist](#10-setup-checklist)
- [11. Failure Modes](#11-failure-modes)
- [12. Interview Questions](#12-interview-questions)
- [References](#references)

---

## 0. One-Minute Version

- **What:** managed Kubernetes control plane (API server, etcd, scheduler) across 3 AZs; you bring worker nodes or Fargate
- **Why:** a portable, extensible platform with a huge ecosystem (Helm, operators, service mesh), same API on any cloud
- **How:** you declare desired state (Deployments, Services); controllers keep reconciling actual state toward it
- **Catch:** many moving parts (networking, IAM mapping, add-ons, upgrades); more power and more operational load than ECS
- 🗣 "Kubernetes is a reconciliation loop: I declare desired state, controllers converge to it; EKS runs the control plane, I own nodes, add-ons and upgrades."

## 1. Architecture

```text
EKS control plane (AWS-managed, multi-AZ): API server, etcd, scheduler, controller manager
          | kubectl / CI talk to the API server
Worker nodes in 3 AZs (managed node groups, Karpenter, or Fargate)
   each node: kubelet + kube-proxy + container runtime (containerd) + VPC CNI
        pods (one or more containers sharing an IP)
```

- etcd stores the cluster state (Raft consensus); the scheduler picks a node per pod; controllers reconcile
- AWS charges per cluster-hour for the control plane plus the nodes (AWS pricing page)

## 2. Core Objects

| Object | In plain words |
|---|---|
| Pod | The smallest unit: one or more containers sharing network and storage |
| Deployment | Keeps N identical pods running; does rolling updates (via ReplicaSets) |
| StatefulSet | Pods with stable names and their own volumes (databases, Kafka) |
| DaemonSet | One pod per node (log agents, monitoring) |
| Job / CronJob | Run-to-completion work, once or on a schedule |
| Service | Stable virtual IP and DNS name in front of a set of pods |
| Ingress / Gateway API | HTTP routing from outside into Services (via the AWS Load Balancer Controller) |
| ConfigMap / Secret | Config and sensitive values mounted or injected into pods |
| Namespace | A folder for objects; unit for quotas and access control |
| PersistentVolume / Claim | Storage that outlives a pod (EBS, EFS) |
| HPA | Horizontal Pod Autoscaler: changes replica count from metrics |

## 3. Compute Options On EKS

| Option | What it is | Good at | Watch out |
|---|---|---|---|
| Managed node groups | EC2 Auto Scaling groups managed by EKS | Simple, AWS-patched AMIs | Scaling via Cluster Autoscaler; one instance shape per group |
| Karpenter | Open-source node provisioner that picks instance types per pending pod | Fast, flexible, cost-efficient bin packing, Spot | Another controller to run and configure |
| Fargate profiles | Each pod in its own microVM, no nodes | No node management | No DaemonSets, limits on storage and privileged pods |
| Self-managed nodes | Your own ASGs and AMIs | Full control | All patching is yours |
| EKS Auto Mode | AWS manages nodes, scaling and core add-ons | Least operational work | Less control; newer (check current features) |

## 4. Scaling: Pods And Nodes

- **In plain words:** first more copies of the app (pods), then more machines to hold them (nodes).

1. **Pods:** HPA scales replicas on CPU, memory or custom metrics (requests per second, queue depth via KEDA)
2. **Nodes:** Cluster Autoscaler (grows the ASG when pods are pending) or Karpenter (launches a fitting instance directly)
3. **Right-sizing:** VPA suggests requests and limits

- Requests vs limits: the scheduler places pods by **requests**; limits cap usage (CPU is throttled, memory over the limit is OOM-killed)
- PodDisruptionBudget: keep at least N pods up during node drains and upgrades
- Topology spread constraints: spread replicas across AZs and nodes

## 5. Networking

- **Amazon VPC CNI:** every pod gets a real VPC IP from the subnet; plan subnet sizes (IP exhaustion is a classic EKS issue); prefix delegation helps
- Service types: `ClusterIP` (internal), `NodePort`, `LoadBalancer` (NLB via the controller)
- **AWS Load Balancer Controller:** turns Ingress objects into ALBs and `LoadBalancer` Services into NLBs; IP-mode targets send traffic straight to pods
- DNS: CoreDNS resolves `orders.default.svc.cluster.local`
- NetworkPolicies restrict pod-to-pod traffic (VPC CNI supports them, or Calico / Cilium)
- Service mesh (Istio, Linkerd) adds mTLS, retries and traffic splitting via sidecars or ambient mode

## 6. Security

- **Who can call the Kubernetes API:** IAM principals mapped to Kubernetes RBAC (EKS access entries; older clusters used the `aws-auth` ConfigMap)
- **What pods can call in AWS:** IRSA (IAM Roles for Service Accounts) or EKS Pod Identity: each service account gets its own IAM role, no node-wide credentials
- RBAC: Roles and RoleBindings per namespace; ClusterRoles sparingly
- Secrets: Kubernetes Secrets are base64, not encrypted by default; enable KMS envelope encryption, or use the Secrets Store CSI driver with Secrets Manager
- Pod Security Standards (baseline / restricted): no privileged pods, non-root, read-only root filesystem
- Private API endpoint, private nodes, image scanning, admission policies (Kyverno, OPA Gatekeeper)

## 7. Deployments And Config

- Rolling update knobs: `maxSurge`, `maxUnavailable`
- Probes
  - **Readiness:** "send me traffic" (removes the pod from the Service while false)
  - **Liveness:** "restart me" (restarts the container when it fails)
  - **Startup:** holds off the other probes during slow JVM starts
- Graceful shutdown: `preStop` hook + `terminationGracePeriodSeconds`; the app handles SIGTERM
- Packaging: Helm charts or Kustomize; GitOps with Argo CD or Flux syncs Git to the cluster
- Progressive delivery: Argo Rollouts / Flagger for canary and blue-green
- Upgrades: control plane first (one minor version at a time), then add-ons, then nodes; Kubernetes minor versions lose standard support after a fixed window, so plan regular upgrades

## 8. Observability

- Metrics: Prometheus (Amazon Managed Prometheus) + Grafana; CloudWatch Container Insights
- Logs: Fluent Bit DaemonSet to CloudWatch, OpenSearch or others
- Traces: OpenTelemetry collector
- Watch: pending pods, OOMKilled and CrashLoopBackOff counts, node pressure, HPA at max, API server errors

## 9. ECS vs EKS

| | ECS | EKS |
|---|---|---|
| What it is | AWS-native scheduler | Managed Kubernetes |
| Learning curve | Low | High |
| Portability | AWS only | Any cloud or on-prem |
| Ecosystem | AWS integrations | Helm, operators, mesh, GitOps, huge CNCF ecosystem |
| Control plane cost | No extra charge | Per-cluster hourly fee |
| Operational load | Low (especially with Fargate) | Higher: add-ons, upgrades, networking |
| Choose when | AWS-only, small team, straightforward services | Many teams, multi-cloud, need Kubernetes-native tooling or operators |

- Default: ECS on Fargate for a small team on AWS; EKS when the organization already runs Kubernetes or needs its ecosystem

## 10. Setup Checklist

1. Cluster: version, private API endpoint, subnets in 3 AZs sized for pod IPs
2. Compute: managed node groups or Karpenter (Spot + on-demand mix), or Fargate profiles
3. Add-ons: VPC CNI, CoreDNS, kube-proxy, EBS CSI driver, AWS Load Balancer Controller, metrics-server
4. Access: access entries / RBAC for humans and CI; IRSA or Pod Identity for workloads
5. Workloads: Deployments with requests / limits, probes, PodDisruptionBudgets, topology spread
6. Scaling: HPA (or KEDA) for pods; Cluster Autoscaler or Karpenter for nodes
7. Ingress: ALB via the controller; TLS certificates from ACM
8. Security: Pod Security Standards, NetworkPolicies, Secrets encryption with KMS, image scanning
9. Observability: metrics, logs, traces, alerts
10. Delivery: Helm or Kustomize + GitOps; upgrade runbook

## 11. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Pods Pending | No node capacity, IP exhaustion, unmatched taints or affinity | `kubectl describe pod` events | Karpenter / autoscaler, larger subnets, prefix delegation |
| CrashLoopBackOff | App crash, bad config, liveness probe too aggressive | Restart counts | Fix config; startup probe; relax liveness |
| OOMKilled | Memory limit below real use | Pod status, exit 137 | Raise limits; size the JVM heap to the container |
| Outage during node upgrade | No PodDisruptionBudget, single replica | Downtime during drains | PDBs, ≥ 2 replicas spread across AZs |
| CPU throttling | Low CPU limits | Latency up, CPU below 100% | Raise or remove CPU limits; set requests correctly |
| Pods with too much AWS access | Node role used by all pods | IAM audit | IRSA / Pod Identity per service account |

## 12. Interview Questions

**Q1. Requests vs limits?**
- L4: requests are what the scheduler reserves; limits are the cap
- L5 extra: CPU over the limit is throttled, memory over the limit is OOM-killed; many teams set memory limit = request and leave CPU limits off to avoid throttling

**Q2. How do pods get AWS permissions?**
- L4: IRSA or EKS Pod Identity maps a Kubernetes service account to an IAM role
- L5 extra: this avoids the node instance role being shared by every pod, so a compromised pod gets only its own permissions

**Q3. When EKS over ECS?**
- L4: when you need portability or the Kubernetes ecosystem
- L5 extra: weigh the extra operational load (upgrades, add-ons, networking) against organizational standards and tooling; small AWS-only teams usually do better on ECS

## References

- [Amazon EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS Best Practices Guide](https://docs.aws.amazon.com/eks/latest/best-practices/introduction.html)
- [Kubernetes documentation — Concepts](https://kubernetes.io/docs/concepts/)
- [Karpenter documentation](https://karpenter.sh/docs/)
