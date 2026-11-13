# 1qs-old — System Design Question Index

> Names only, grouped. Base: `D:\1lc\1sd02`. Merged in: `D:\1lc\1o\2.sd`.
> `-1o` = only in the Oracle set. `(= …)` = the Oracle set's name for a merged duplicate.
> Last updated: 2026-11-11

## Index
- [0. Foundations](#0-foundations)
- [1. Core Building Blocks](#1-core-building-blocks)
- [2. Social Media](#2-social-media)
- [3. Commerce, Marketplace, Geo](#3-commerce-marketplace-geo)
- [4. Collaboration and Productivity](#4-collaboration-and-productivity)
- [5. Media and Realtime](#5-media-and-realtime)
- [6. Data Platform and Search](#6-data-platform-and-search)
- [7. Infrastructure and DevEx](#7-infrastructure-and-devex)
- [8. Fintech and Trust](#8-fintech-and-trust)
- [9. AI and Search](#9-ai-and-search)
- [10. Enterprise and Security](#10-enterprise-and-security)
- [11. PKI and Key Management](#11-pki-and-key-management)
- [12. Counts](#12-counts)

---

## 0. Foundations
- Concepts, not design prompts
- SDE Overview
- FR / NFR
- Back-of-the-envelope Estimation
- High-level Architecture
- API Design
- Data Modeling
- Database
- Caching
- Messaging
- Consistency
- Partitioning
- Reliability
- Observability
- Security
- Performance and Capacity
- Scale From Zero To Millions Of Users
- A Framework For System Design Interviews
- HA and SLA -1o

## 1. Core Building Blocks
- Rate Limiter (= Distributed Rate Limiter)
- Consistent Hashing
- Key-value Store
- Strongly Consistent Metadata KV Store -1o
- Unique ID Generator
- URL Shortener
- Distributed Cache
- Thread-safe LRU Cache -1o
- API Gateway
- Load Balancer (= Software Load Balancer)
- CDN
- Feature Flag Service
- Distributed Lock Service (= Distributed Lease and Lock Service)
- Distributed Message Queue (= Durable Distributed Event Log)
- S3-like Object Storage (= Distributed Object Storage)
- DB Connection Pool -1o
- Scale a Monolithic Service -1o

## 2. Social Media
- News Feed System
- Follow/Unfollow and Timeline Fanout
- Social Graph Service
- Chat System
- Group Chat
- Presence Service
- Nearby Friends
- Stories/Reels Ranking Pipeline
- Instagram
- Tinder
- Pinterest
- Reddit

## 3. Commerce, Marketplace, Geo
- Order Management
- Inventory Management
- Checkout and Payment Orchestration
- Product Catalog
- Shopping Cart
- Amazon E-commerce Platform
- E-commerce Recommendation Service (= E-commerce Recommendations)
- Airbnb
- Hotel Reservation System
- Parking Garage System
- Uber / Ride Matching (= Uber Ride Matching)
- Food Delivery Platform
- Proximity Service
- Google Maps

## 4. Collaboration and Productivity
- Google Drive
- Fault-tolerant File Upload -1o
- Collaborative Document Editor
- Calendar Scheduling
- Meeting Room Booking
- Task Management Platform
- Pastebin Service
- Notification System
- Notification Inbox
- Distributed Email Service

## 5. Media and Realtime
- YouTube (= Global Video Streaming)
- Live Streaming Platform
- Video Call Service
- Audio Call Service
- WebSocket Gateway at Scale
- Realtime Multiplayer Lobby
- Real-time Gaming Leaderboard
- Warcraft 3 Replays
- Image Processing Pipeline
- Ad Serving System
- Ad Impression Tracking
- Ad Click Event Aggregation
- CDN Log Processing Pipeline

## 6. Data Platform and Search
- Web Crawler
- Search Autocomplete System
- Google Search
- Full-text Search Service
- Time-series Storage Service
- Metrics Monitoring and Alerting (= Internal Metrics Ingestion)
- Clickstream Analytics Platform
- Real-time Analytics Pipeline
- Realtime Fraud Detection Pipeline
- IoT Telemetry Platform
- ETL Orchestration for Warehouse
- Healthcare Ingestion Pipeline -1o
- Recommendation Engine
- Recommendation Feature Store

## 7. Infrastructure and DevEx
- Service Discovery
- Configuration Management Service (= Versioned Configuration Distribution)
- Secrets Management Service
- Distributed Task Scheduler (= Distributed Job Scheduler)
- Container Scheduler
- CI Build Queue
- Artifact Repository
- Distributed Tracing Backend
- Multi-tenant Logging Platform
- Logging File System -1o
- Edge Device Health Monitoring -1o
- Async Control-plane Resource API -1o

## 8. Fintech and Trust
- Payment System
- Digital Wallet
- Double-entry Accounting Platform
- Card Authorization System
- Billing and Invoicing Platform
- Risk Scoring Service
- KYC Workflow Service
- AML Monitoring Pipeline
- Stock Exchange

## 9. AI and Search
- RAG Platform
- Vector Retrieval Service
- Vector Embedding Service
- Model Inference Gateway
- Prompt Caching Service
- Online Feature Store for ML
- Personalization Engine
- Experimentation Platform

## 10. Enterprise and Security
- RBAC/ABAC Authorization Service
- SSO Identity Provider
- Zero Trust Access Proxy
- Remote Browser Isolation -1o
- Tenant Isolation for SaaS
- Audit Logging System
- Data Loss Prevention Scanner
- Compliance Evidence Collector
- Multi-region Backup and Restore Service

## 11. PKI and Key Management
- Whole group is from the Oracle set
- PKI / KMS Mechanisms -1o
- Multi-tenant Certificate Authority -1o
- Certificate Renewal and CA Rollover -1o
- Certificate Revocation (CRL / OCSP) -1o
- HSM Key Management and Signing -1o
- Certificate and Key Authorization -1o
- Regional PKI Disaster Recovery -1o

## 12. Counts

| Group | Questions | -1o |
|---|---|---|
| 1–10 design groups | 118 | 10 |
| 11 PKI | 7 | 7 |
| Total questions | 125 | 17 |

- Foundations (§0): 18 concepts, 1 of them -1o
- Oracle-set duplicates merged: 14
  - 11 shown as `(= …)`
  - 3 had the same name: Chat System, URL Shortener, Warcraft 3 Replays
