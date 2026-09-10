# System Design Question Index

Authoritative, deduplicated map for 107 design questions plus three Alex Xu foundation chapters.

- `1AX/` owns concepts and questions covered by Alex Xu's *System Design Interview — An Insider's Guide*, Volumes 1 and 2.
- `01.core/` through `10.enterprise security/` contain non-duplicate questions grouped by domain.
- `00.base/` contains reusable system-design knowledge rather than question packets.
- Read a packet only after a cold attempt. Follow [`build.md`](./build.md) when generating or updating answer content.

## 1AX — Alex Xu

Chapter names follow the published book tables of contents.

### Volume 1 foundations — concepts, not standalone design prompts

1. [Scale From Zero To Millions Of Users](./1AX/AX1-01.scale-from-zero-to-millions-of-users.md)
2. [Back-of-the-envelope Estimation](./1AX/AX1-02.back-of-the-envelope-estimation.md)
3. [A Framework For System Design Interviews](./1AX/AX1-03.a-framework-for-system-design-interviews.md)

### Volume 1 design questions

4. [Design A Rate Limiter](./1AX/AX1-04.design-a-rate-limiter.md)
5. [Design Consistent Hashing](./1AX/AX1-05.design-consistent-hashing.md)
6. [Design A Key-value Store](./1AX/AX1-06.design-a-key-value-store.md)
7. [Design A Unique Id Generator In Distributed Systems](./1AX/AX1-07.design-a-unique-id-generator-in-distributed-systems.md)
8. [Design A Url Shortener](./1AX/AX1-08.design-a-url-shortener.md)
9. [Design A Web Crawler](./1AX/AX1-09.design-a-web-crawler.md)
10. [Design A Notification System](./1AX/AX1-10.design-a-notification-system.md)
11. [Design A News Feed System](./1AX/AX1-11.design-a-news-feed-system.md)
12. [Design A Chat System](./1AX/AX1-12.design-a-chat-system.md)
13. [Design A Search Autocomplete System](./1AX/AX1-13.design-a-search-autocomplete-system.md)
14. [Design Youtube](./1AX/AX1-14.design-youtube.md)
15. [Design Google Drive](./1AX/AX1-15.design-google-drive.md)

### Volume 2

1. [Proximity Service](./1AX/AX2-01.proximity-service.md)
2. [Nearby Friends](./1AX/AX2-02.nearby-friends.md)
3. [Google Maps](./1AX/AX2-03.google-maps.md)
4. [Distributed Message Queue](./1AX/AX2-04.distributed-message-queue.md)
5. [Metrics Monitoring and Alerting System](./1AX/AX2-05.metrics-monitoring-and-alerting-system.md)
6. [Ad Click Event Aggregation](./1AX/AX2-06.ad-click-event-aggregation.md)
7. [Hotel Reservation System](./1AX/AX2-07.hotel-reservation-system.md)
8. [Distributed Email Service](./1AX/AX2-08.distributed-email-service.md)
9. [S3-like Object Storage](./1AX/AX2-09.s3-like-object-storage.md)
10. [Real-time Gaming Leaderboard](./1AX/AX2-10.real-time-gaming-leaderboard.md)
11. [Payment System](./1AX/AX2-11.payment-system.md)
12. [Digital Wallet](./1AX/AX2-12.digital-wallet.md)
13. [Stock Exchange](./1AX/AX2-13.stock-exchange.md)

## 01. Core

- [Distributed Cache](./01.core/0103.distributed-cache.md)
- [API Gateway](./01.core/0105.api-gateway.md)
- [Feature Flag Service](./01.core/0106.feature-flag-service.md)
- [Distributed Lock Service](./01.core/0108.distributed-lock-service.md)
- [CDN](./01.core/0109.cdn.md)
- [Load Balancer](./01.core/0110.load-balancer.md)

## 02. Social Media

- [Follow/Unfollow and Timeline Fanout](./02.social-media/0203.follow-unfollow-timeline-fanout.md)
- [Social Graph Service](./02.social-media/0204.social-graph-service.md)
- [Group Chat](./02.social-media/0205.group-chat.md)
- [Presence Service](./02.social-media/0207.presence-service.md)
- [Stories/Reels Ranking Pipeline](./02.social-media/0208.stories-reels-ranking-pipeline.md)
- [Instagram](./02.social-media/0209.instagram.md)
- [Tinder](./02.social-media/0210.tinder.md)
- [Pinterest](./02.social-media/0211.pinterest.md)
- [Reddit](./02.social-media/0212.reddit.md)

## 03. Commerce and Marketplace

- [Order Management](./03.commerce%20marketplace/0301.order-management.md)
- [Inventory Management](./03.commerce%20marketplace/0302.inventory-management.md)
- [Checkout and Payment Orchestration](./03.commerce%20marketplace/0303.checkout-payment-orchestration.md)
- [Product Catalog](./03.commerce%20marketplace/0304.product-catalog.md)
- [Shopping Cart](./03.commerce%20marketplace/0305.shopping-cart.md)
- [Uber / Ride Sharing](./03.commerce%20marketplace/0306.ride-matching-platform.md)
- [Food Delivery Platform](./03.commerce%20marketplace/0307.food-delivery-platform.md)
- [E-commerce Recommendation Service](./03.commerce%20marketplace/0308.ecommerce-recommendation-service.md)
- [Airbnb](./03.commerce%20marketplace/0309.airbnb.md)
- [Amazon E-commerce Platform](./03.commerce%20marketplace/0310.amazon-ecommerce-platform.md)
- [Parking Garage System](./03.commerce%20marketplace/0311.parking-garage-system.md)

## 04. Collaboration and Productivity

- [Calendar Scheduling](./04.collaboration%20productivity/0401.calendar-scheduling.md)
- [Collaborative Document Editor](./04.collaboration%20productivity/0403.collaborative-document-editor.md)
- [Task Management Platform](./04.collaboration%20productivity/0405.task-management-platform.md)
- [Meeting Room Booking](./04.collaboration%20productivity/0406.meeting-room-booking.md)
- [Pastebin Service](./04.collaboration%20productivity/0407.pastebin-service.md)
- [Notification Inbox](./04.collaboration%20productivity/0408.notification-inbox.md)

## 05. Media and Realtime

- [Video Call Service](./05.media%20realtime/0502.video-call-service.md)
- [Live Streaming Platform](./05.media%20realtime/0503.live-streaming-platform.md)
- [Audio Call Service](./05.media%20realtime/0504.audio-call-service.md)
- [Ad Impression Tracking](./05.media%20realtime/0505.ad-impression-tracking.md)
- [WebSocket Gateway at Scale](./05.media%20realtime/0506.websocket-gateway-scale.md)
- [CDN Log Processing Pipeline](./05.media%20realtime/0507.cdn-log-processing-pipeline.md)
- [Realtime Multiplayer Lobby](./05.media%20realtime/0508.realtime-multiplayer-lobby.md)
- [Ad Serving System](./05.media%20realtime/0509.ad-serving-system.md)
- [Image Processing Pipeline](./05.media%20realtime/0510.image-processing-pipeline.md)

## 06. Data Platform

- [Full-text Search Service](./06.data%20platform/0602.fulltext-search-service.md)
- [Time-series Storage Service](./06.data%20platform/0604.timeseries-storage-service.md)
- [Clickstream Analytics Platform](./06.data%20platform/0605.clickstream-analytics-platform.md)
- [Realtime Fraud Detection Pipeline](./06.data%20platform/0606.realtime-fraud-detection-pipeline.md)
- [Recommendation Feature Store](./06.data%20platform/0607.recommendation-feature-store.md)
- [ETL Orchestration for Warehouse](./06.data%20platform/0608.etl-orchestration-warehouse.md)
- [Google Search](./06.data%20platform/0609.google-search.md)
- [Recommendation Engine](./06.data%20platform/0610.recommendation-engine.md)
- [IoT Telemetry Platform](./06.data%20platform/0611.iot-telemetry-platform.md)
- [Real-time Analytics Pipeline](./06.data%20platform/0612.realtime-analytics-pipeline.md)

## 07. Infrastructure and DevEx

- [Service Discovery](./07.infra%20devex/0701.service-discovery.md)
- [Secrets Management Service](./07.infra%20devex/0702.secrets-management-service.md)
- [Configuration Management Service](./07.infra%20devex/0703.configuration-management-service.md)
- [Distributed Tracing Backend](./07.infra%20devex/0704.distributed-tracing-backend.md)
- [Container Scheduler](./07.infra%20devex/0705.container-scheduler.md)
- [Multi-tenant Logging Platform](./07.infra%20devex/0706.multitenant-logging-platform.md)
- [CI Build Queue](./07.infra%20devex/0707.ci-build-queue.md)
- [Artifact Repository](./07.infra%20devex/0708.artifact-repository.md)
- [Distributed Task Scheduler](./07.infra%20devex/0709.distributed-task-scheduler.md)

## 08. Fintech and Trust

- [Double-entry Accounting Platform](./08.fintech%20trust/0803.double-entry-accounting-platform.md)
- [Card Authorization System](./08.fintech%20trust/0804.card-authorization-system.md)
- [Risk Scoring Service](./08.fintech%20trust/0805.risk-scoring-service.md)
- [KYC Workflow Service](./08.fintech%20trust/0806.kyc-workflow-service.md)
- [Billing and Invoicing Platform](./08.fintech%20trust/0807.billing-invoicing-platform.md)
- [AML Monitoring Pipeline](./08.fintech%20trust/0808.aml-monitoring-pipeline.md)

## 09. AI and Search

- [RAG Platform](./09.ai%20search/0901.rag-platform.md)
- [Vector Retrieval Service](./09.ai%20search/0902.vector-retrieval-service.md)
- [Model Inference Gateway](./09.ai%20search/0903.model-inference-gateway.md)
- [Experimentation Platform](./09.ai%20search/0904.experimentation-platform.md)
- [Personalization Engine](./09.ai%20search/0905.personalization-engine.md)
- [Vector Embedding Service](./09.ai%20search/0906.vector-embedding-service.md)
- [Prompt Caching Service](./09.ai%20search/0907.prompt-caching-service.md)
- [Online Feature Store for ML](./09.ai%20search/0908.online-feature-store-ml.md)

## 10. Enterprise and Security

- [RBAC/ABAC Authorization Service](./10.enterprise%20security/1001.rbac-abac-authorization-service.md)
- [SSO Identity Provider](./10.enterprise%20security/1002.sso-identity-provider.md)
- [Audit Logging System](./10.enterprise%20security/1003.audit-logging-system.md)
- [Zero Trust Access Proxy](./10.enterprise%20security/1004.zero-trust-access-proxy.md)
- [Tenant Isolation for SaaS](./10.enterprise%20security/1005.tenant-isolation-saas.md)
- [Multi-region Backup and Restore Service](./10.enterprise%20security/1006.multiregion-backup-restore-service.md)
- [Data Loss Prevention Scanner](./10.enterprise%20security/1007.data-loss-prevention-scanner.md)
- [Compliance Evidence Collector](./10.enterprise%20security/1008.compliance-evidence-collector.md)
