# Alex Xu System Design Question Bank (Interview-Ready)

This folder tracks canonical system design questions from Alex Xu's books and provides deep, interview-ready solution packets.

## Index

| # | Question | Book | Scope | Solution |
| --- | --- | --- | --- | --- |
| 01 | Rate Limiter | Vol 1 | Design a multi-tenant distributed rate limiter with hard/soft quotas, burst allowance, and hierarchical limits. | [Open](./solutions/ax01.rate-limiter.md) |
| 02 | Consistent Hashing | Vol 1 | Design shard placement and rebalancing with bounded data movement and skew control. | [Open](./solutions/ax02.consistent-hashing.md) |
| 03 | Key-Value Store | Vol 1 | Design a globally distributed KV store with tunable consistency and anti-entropy repair. | [Open](./solutions/ax03.key-value-store.md) |
| 04 | Unique ID Generator | Vol 1 | Design a Snowflake-like ID service with region failover and clock rollback handling. | [Open](./solutions/ax04.unique-id-generator.md) |
| 05 | URL Shortener | Vol 1 | Design TinyURL-scale shortening with abuse controls, analytics, and custom aliases. | [Open](./solutions/ax05.url-shortener.md) |
| 06 | Web Crawler | Vol 1 | Design a web crawler with politeness, deduplication, recrawl scheduling, and spam control. | [Open](./solutions/ax06.web-crawler.md) |
| 07 | Notification System | Vol 1 | Design omnichannel notifications (push/email/SMS/in-app) with preference and delivery guarantees. | [Open](./solutions/ax07.notification-system.md) |
| 08 | News Feed System | Vol 1 | Design social feed generation with hybrid fanout, ranking hooks, and cache invalidation. | [Open](./solutions/ax08.news-feed-system.md) |
| 09 | Chat System | Vol 1 | Design 1:1 + group chat with ordering semantics, online presence, and media attachments. | [Open](./solutions/ax09.chat-system.md) |
| 10 | Proximity Service | Vol 2 | Design geospatial nearest-neighbor service for moving entities with geo-index strategy. | [Open](./solutions/ax10.proximity-service.md) |
| 11 | Nearby Friends | Vol 2 | Design privacy-aware real-time nearby-friends detection and subscription updates. | [Open](./solutions/ax11.nearby-friends.md) |
| 12 | Google Maps | Vol 2 | Design map tiles + routing + traffic ingestion for low-latency navigation queries. | [Open](./solutions/ax12.google-maps.md) |
| 13 | Distributed Message Queue | Vol 2 | Design partitioned durable pub/sub queue with replay, consumer groups, and backpressure. | [Open](./solutions/ax13.distributed-message-queue.md) |
| 14 | Metrics Monitoring & Alerting | Vol 2 | Design TSDB-backed metrics platform with cardinality controls and SLO alert semantics. | [Open](./solutions/ax14.metrics-monitoring-and-alerting.md) |
| 15 | Ad Click Event Aggregation | Vol 2 | Design stream + batch aggregation pipeline for ads billing and fraud-aware counting. | [Open](./solutions/ax15.ad-click-event-aggregation.md) |
| 16 | Hotel Reservation System | Vol 2 | Design inventory/booking system preventing overbooking under high contention. | [Open](./solutions/ax16.hotel-reservation-system.md) |
| 17 | Distributed Email Service | Vol 2 | Design outbound email platform with retries, reputation management, and template rendering. | [Open](./solutions/ax17.distributed-email-service.md) |
| 18 | S3-like Object Storage | Vol 2 | Design object storage for durability, multipart upload, lifecycle tiers, and replication. | [Open](./solutions/ax18.s3-like-object-storage.md) |
| 19 | Real-time Gaming Leaderboard | Vol 2 | Design leaderboard with rank queries, seasonal resets, anti-cheat event ingestion. | [Open](./solutions/ax19.real-time-gaming-leaderboard.md) |
| 20 | Payment System | Vol 2 | Design payment orchestration and ledger-safe state machine for authorizations/captures/refunds. | [Open](./solutions/ax20.payment-system.md) |
| 21 | Digital Wallet | Vol 2 | Design wallet with double-entry ledger, idempotent transfers, and risk/fraud hooks. | [Open](./solutions/ax21.digital-wallet.md) |
| 22 | Stock Exchange | Vol 2 | Design matching engine + market data dissemination with deterministic sequencing. | [Open](./solutions/ax22.stock-exchange.md) |
