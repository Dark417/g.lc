# 03db.01aurora.01architecture Why Aurora And Its Storage

> Aurora moves replication from the database engine into a shared, 6-way quorum storage layer that only receives redo log records.

## Index

- [1. Why Aurora Exists](#1-why-aurora-exists)
  - [1.1 Pain Before It](#11-pain-before-it)
  - [1.2 Insight In The Paper](#12-insight-in-the-paper)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. The Log Is The Database](#2-the-log-is-the-database)
  - [2.1 Segments And Write Path](#21-segments-and-write-path)
  - [2.2 Quorum Math](#22-quorum-math)
  - [2.3 Reads And Repair](#23-reads-and-repair)
  - [2.4 Picture](#24-picture)
- [Related](#related)

## 1. Why Aurora Exists

Classic Postgres High Availability (HA) copies whole pages and Write-Ahead Log (WAL) to standbys with their own disks; Aurora was built to stop that.

### 1.1 Pain Before It

- Setup: Postgres or MySQL on network block storage (Elastic Block Store, EBS) with a synchronous standby
- Each write sends a lot over the network
  - WAL record
  - Data page
  - Full-page image
  - Standby copy
  - Result: write amplification over the network
- Paper's measurement (MySQL-based Aurora vs mirrored MySQL, Special Interest Group on Management of Data (SIGMOD) 2017, Table 1)
  - 35× more transactions
  - 7.7× fewer I/Os per transaction
  - Limit: one benchmark from the authors, MySQL engine, 2017 hardware
- Adding a read replica copied the whole dataset
  - And replayed WAL on its own disk
- Failover = promote a standby that may need crash recovery

### 1.2 Insight In The Paper

- The bottleneck moved from Central Processing Unit (CPU)/disk to the network between compute and storage
- So send the smallest thing possible over the network: the redo log

### 1.3 Common Use Cases

- Online Transaction Processing (OLTP) services that outgrew one Relational Database Service (RDS) instance's read capacity
- Systems needing fast failover with no data loss inside one Region
- Spiky or dev/test workloads on Serverless v2
  - See [04serverless-v2](01aurora.04serverless-v2.md)

## 2. The Log Is The Database

The writer ships only redo records; storage nodes turn them into pages in the background.

### 2.1 Segments And Write Path

- Volume is split into 10 gigabytes (GB) segments
- Each segment = a protection group of 6 copies
  - 2 copies per Availability Zone (AZ), 3 AZs
- Write path

  → Writer generates redo log records for a transaction  
  → Sends them to all 6 storage nodes of each affected segment  
  → Commit is acknowledged once 4 of 6 nodes persisted the records  
  → Storage nodes later coalesce log records into data pages in the background  
  ⇒ No page writes, no checkpoint I/O, no full-page writes from the writer

### 2.2 Quorum Math

Paper, §2.1.

- V = 6, write quorum Vw = 4, read quorum Vr = 3
- Vw + Vr > V
  - Result: every read quorum overlaps the latest write
- 2·Vw > V
  - Result: two writes cannot both succeed on disjoint sets
- Lose a whole AZ (2 copies) + 1 more node
  - 3 left ⇒ still readable, data intact
- Lose a whole AZ
  - 4 left ⇒ still writable

### 2.3 Reads And Repair

- Limit: normal reads do **not** use a 3/6 quorum
  - Writer knows which segments are current and reads one (paper §4.2.3)
  - The read quorum is used when rebuilding state during recovery
- Small segments make repair fast
  - Paper: a 10 GB segment repairs in about 10 s on a 10 Gbps link
  - Short repair window ⇒ low chance of a second failure before repair finishes

### 2.4 Picture

```text
       app: writer pool                    app: reader pool
            |                                    |
   cluster endpoint (CNAME)          reader endpoint (DNS round-robin)
            |                                    |
   +----------------+                   +----------------+
   | writer (AZ-a)  |                   | reader (AZ-b)  |
   +-------+--------+                   +-------+--------+
           | redo log records only              | page reads on cache miss
           v                                    v
   +-------------------------------------------------------+
   | shared cluster volume, 10 GB segments x 6 copies      |
   |   AZ-a: [c1][c2]    AZ-b: [c3][c4]    AZ-c: [c5][c6]  |
   |   commit ack at 4/6         recovery read at 3/6      |
   +-------------------------------------------------------+
```

Notice that the writer never ships pages: replicas read pages from the same volume, so adding one copies no data.

- The app side of this picture (two pools, one per endpoint) is wired in [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)
- 🗣 "Aurora moves replication from the database to the storage layer: the writer ships redo log records, and storage turns them into pages."

## Related

- [00index](01aurora.00index.md)
- [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md)
- [03failover-dns](01aurora.03failover-dns.md)
