# Snowflake E2E Observability Framework
## Design Document v1.0

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Module Specifications](#3-module-specifications)
4. [Data Flow Architecture](#4-data-flow-architecture)
5. [Implementation Guide](#5-implementation-guide)
6. [Security Considerations](#6-security-considerations)
7. [Operations & Maintenance](#7-operations--maintenance)
8. [Appendix](#8-appendix)

---

## 1. Executive Summary

### 1.1 Purpose
This document provides the comprehensive design specification for the Snowflake E2E Observability Framework, a unified monitoring and governance solution that delivers complete visibility across the Snowflake data platform.

### 1.2 Scope
The framework covers 10 critical observability domains:

| Domain | Primary Focus |
|--------|--------------|
| Platform Performance | Warehouse utilization, query execution, resource optimization |
| Pipeline Reliability | Data freshness, task monitoring, ingestion health |
| FinOps & Cost Intelligence | Credit consumption, cost allocation, budget management |
| Data Quality & Trust | Data validation, anomaly detection, quality scoring |
| Security & Access | Authentication, authorization, access auditing |
| Metadata & Lineage | Data lineage, object dependencies, impact analysis |
| User & Workload Behavior | Usage patterns, capacity planning, optimization |
| Alerting & Remediation | Proactive alerts, automated responses |
| Executive Dashboards | KPIs, SLA compliance, health scores |
| Governance & Automation | Policy enforcement, standardization, automation |

### 1.3 Target Audience
- Data Platform Engineers
- DataOps/Platform Teams
- FinOps Teams
- Security & Compliance Teams
- Data Governance Teams
- Executive Leadership

### 1.4 Key Benefits
- **Unified Visibility**: Single pane of glass across all platform dimensions
- **Proactive Monitoring**: Catch issues before they impact business
- **Cost Optimization**: Identify waste and optimize resource utilization
- **Compliance Assurance**: Automated governance and audit trails
- **Operational Excellence**: Reduce MTTR and improve platform reliability

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SNOWFLAKE OBSERVABILITY FRAMEWORK                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐              │
│  │   DATA SOURCES   │    │ PROCESSING LAYER │    │ PRESENTATION     │              │
│  │                  │    │                  │    │                  │              │
│  │ • Account Usage  │───▶│ • Views          │───▶│ • Snowsight      │              │
│  │ • Org Usage      │    │ • Dynamic Tables │    │ • Streamlit      │              │
│  │ • Reader Usage   │    │ • Stored Procs   │    │ • BI Tools       │              │
│  │ • Info Schema    │    │ • UDFs           │    │ • REST APIs      │              │
│  │ • Event Tables   │    │                  │    │                  │              │
│  │ • Custom Tables  │    │                  │    │                  │              │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘              │
│           │                       │                       │                         │
│           │              ┌────────▼────────┐              │                         │
│           │              │   ALERTING &    │              │                         │
│           └─────────────▶│   AUTOMATION    │◀─────────────┘                         │
│                          │                 │                                         │
│                          │ • Native Alerts │                                         │
│                          │ • Scheduled     │                                         │
│                          │   Tasks         │                                         │
│                          │ • Notifications │                                         │
│                          │ • Webhooks      │                                         │
│                          └─────────────────┘                                         │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SCHEMA: OBSERVABILITY                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   VIEWS (28)                    TABLES (6)                   PROCEDURES (2)         │
│   ──────────                    ──────────                   ──────────────         │
│   V_WAREHOUSE_PERFORMANCE_*     T_DATA_QUALITY_RULES         SP_RUN_DATA_QUALITY_   │
│   V_QUERY_PERFORMANCE_*         T_DATA_QUALITY_RESULTS         CHECK                │
│   V_TASK_EXECUTION_*            T_ALERT_CONFIG               SP_CLEANUP_            │
│   V_CREDIT_CONSUMPTION_*        T_ALERT_HISTORY                OBSERVABILITY_DATA   │
│   V_LOGIN_ACTIVITY              T_GOVERNANCE_POLICIES                               │
│   V_DATA_ACCESS_PATTERNS        T_GOVERNANCE_AUDIT_LOG       ALERTS (5)             │
│   V_OBJECT_DEPENDENCIES                                      ──────────             │
│   V_USER_ACTIVITY_HEATMAP       TASKS (2)                    ALERT_LONG_RUNNING_    │
│   V_PLATFORM_HEALTH_SCORE       ──────────                     QUERY                │
│   V_EXECUTIVE_SUMMARY           TASK_WEEKLY_CLEANUP          ALERT_FAILED_TASK      │
│   V_SLA_COMPLIANCE              TASK_DAILY_HEALTH_CHECK      ALERT_HIGH_CREDIT_     │
│   ...                                                          USAGE                │
│                                                              ALERT_FAILED_LOGINS    │
│                                                              ALERT_QUEUE_TIME_SPIKE │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Data Source Inventory

| Source | Description | Latency | Retention |
|--------|-------------|---------|-----------|
| `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` | Query execution details | 45 min | 365 days |
| `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` | Credit consumption | 3 hours | 365 days |
| `SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY` | Authentication events | 2 hours | 365 days |
| `SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY` | Data access lineage | 3 hours | 365 days |
| `SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY` | Task execution logs | 45 min | 365 days |
| `SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY` | Data loading history | 45 min | 365 days |
| `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE` | Storage metrics | 24 hours | 365 days |
| `INFORMATION_SCHEMA.*` | Real-time metadata | Real-time | Current |

---

## 3. Module Specifications

### 3.1 Module 1: Platform Performance Monitoring

#### Purpose
Monitor warehouse performance, query execution efficiency, and resource utilization to identify bottlenecks and optimization opportunities.

#### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Query Success Rate | % of queries completing successfully | >99.5% | <99% |
| Avg Query Duration | Mean execution time | <30s | >60s |
| Queue Time | Time queries spend waiting | <5s | >30s |
| Compilation Ratio | Compile time vs execution time | <20% | >40% |
| Concurrent Queries | Simultaneous query count | By WH size | >2x capacity |

#### Views

| View Name | Purpose | Refresh Frequency |
|-----------|---------|-------------------|
| `V_WAREHOUSE_PERFORMANCE_SUMMARY` | Daily warehouse metrics aggregation | On query |
| `V_QUERY_PERFORMANCE_DISTRIBUTION` | Query duration bucketing analysis | On query |
| `V_LONG_RUNNING_QUERIES` | Queries exceeding 5-minute threshold | On query |
| `V_WAREHOUSE_SCALING_EVENTS` | Auto-scaling event tracking | On query |
| `V_COMPILATION_EXECUTION_ANALYSIS` | Compile vs execute time breakdown | On query |

#### Data Model

```
V_WAREHOUSE_PERFORMANCE_SUMMARY
├── WAREHOUSE_NAME (VARCHAR)
├── REPORT_DATE (DATE)
├── TOTAL_QUERIES (NUMBER)
├── AVG_ELAPSED_SEC (NUMBER)
├── MEDIAN_ELAPSED_SEC (NUMBER)
├── MAX_ELAPSED_SEC (NUMBER)
├── AVG_QUEUE_SEC (NUMBER)
├── QUEUED_QUERY_COUNT (NUMBER)
├── QUEUE_PERCENTAGE (NUMBER)
├── AVG_GB_SCANNED (NUMBER)
├── TOTAL_TB_SCANNED (NUMBER)
├── AVG_ROWS_PRODUCED (NUMBER)
├── UNIQUE_USERS (NUMBER)
└── UNIQUE_QUERY_TAGS (NUMBER)
```

---

### 3.2 Module 2: Pipeline Reliability & Freshness Monitoring

#### Purpose
Ensure data pipelines operate reliably, detect stale data, and maintain SLA compliance for data freshness.

#### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Task Success Rate | % of tasks completing successfully | >99% | <95% |
| Data Freshness | Time since last data update | <SLA | >SLA+buffer |
| Pipeline Latency | End-to-end pipeline duration | <target | >2x target |
| File Load Success | % of files loaded successfully | >99.9% | <99% |
| Stream Lag | Pending rows in streams | <1000 | >10000 |

#### Views

| View Name | Purpose |
|-----------|---------|
| `V_TASK_EXECUTION_SUMMARY` | Aggregated task execution metrics |
| `V_FAILED_TASKS_DETAIL` | Detailed failed task analysis |
| `V_TABLE_FRESHNESS` | Data freshness classification |
| `V_COPY_HISTORY_SUMMARY` | Data loading performance |
| `V_SNOWPIPE_PERFORMANCE` | Continuous ingestion metrics |

#### Freshness Classification Logic

```
FRESHNESS_STATUS = CASE
    WHEN hours_since_update <= 1   THEN 'FRESH'
    WHEN hours_since_update <= 24  THEN 'RECENT'
    WHEN hours_since_update <= 168 THEN 'STALE'
    ELSE 'VERY_STALE'
END
```

---

### 3.3 Module 3: FinOps & Cost Intelligence

#### Purpose
Track credit consumption, optimize costs, enable chargeback/showback, and forecast spending.

#### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Daily Credit Burn | Credits consumed per day | <budget | >110% budget |
| Cost per Query | Average credit per query | Baseline | >2x baseline |
| Storage Growth | Monthly storage increase | <10% MoM | >25% MoM |
| Idle Warehouse Time | Time warehouses run without queries | <10% | >30% |
| Cloud Services Ratio | Cloud services vs compute credits | <10% | >15% |

#### Views

| View Name | Purpose |
|-----------|---------|
| `V_CREDIT_CONSUMPTION_WAREHOUSE` | Credits by warehouse (daily) |
| `V_CREDIT_CONSUMPTION_USER` | Credits by user attribution |
| `V_SERVERLESS_COSTS` | Serverless feature consumption |
| `V_STORAGE_USAGE_TRENDS` | Storage growth analysis |
| `V_DATABASE_STORAGE_BREAKDOWN` | Per-database storage costs |
| `V_COST_PER_QUERY` | Query-level cost attribution |
| `V_MONTHLY_COST_SUMMARY` | Month-over-month trending |

#### Cost Attribution Model

```
┌─────────────────────────────────────────────────────────────┐
│                    COST ATTRIBUTION                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   COMPUTE CREDITS                    STORAGE CREDITS         │
│   ───────────────                    ───────────────         │
│   │                                  │                       │
│   ├── By Warehouse ──┐               ├── By Database         │
│   │                  │               ├── By Schema           │
│   ├── By User ───────┤               ├── By Time Travel      │
│   │                  │               └── By Fail-safe        │
│   ├── By Query Tag ──┤                                       │
│   │                  │               SERVERLESS CREDITS      │
│   ├── By Query Type ─┤               ─────────────────       │
│   │                  │               ├── Snowpipe            │
│   └── By Database ───┘               ├── Auto-clustering     │
│                                      ├── Materialized Views  │
│                                      └── Search Optimization │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.4 Module 4: Data Quality & Trust Metrics

#### Purpose
Monitor data quality dimensions, detect anomalies, track schema changes, and maintain data trust scores.

#### Quality Dimensions

| Dimension | Description | Measurement |
|-----------|-------------|-------------|
| Completeness | Missing/null values | NULL rate per column |
| Uniqueness | Duplicate records | Duplicate count/ratio |
| Validity | Values within expected range | Range violation count |
| Consistency | Cross-table integrity | Referential integrity checks |
| Timeliness | Data freshness | Age of newest record |
| Accuracy | Correctness of values | Pattern/format validation |

#### Tables

| Table Name | Purpose |
|------------|---------|
| `T_DATA_QUALITY_RULES` | Quality rule configuration |
| `T_DATA_QUALITY_RESULTS` | Quality check execution results |

#### Rule Types Supported

```sql
RULE_TYPE IN (
    'NULL_CHECK',      -- Check for null/missing values
    'UNIQUE_CHECK',    -- Check for duplicates
    'RANGE_CHECK',     -- Validate numeric ranges
    'PATTERN_CHECK',   -- Regex pattern validation
    'FRESHNESS_CHECK', -- Data age validation
    'REFERENTIAL_CHECK' -- Foreign key validation
)
```

#### Quality Score Calculation

```
Quality Score = Σ(Rule_Weight × Pass_Rate) / Σ(Rule_Weight)

Where:
- Pass_Rate = (Total_Rows - Failed_Rows) / Total_Rows
- Rule_Weight = Based on business criticality (1-10)
```

---

### 3.5 Module 5: Security & Access Monitoring

#### Purpose
Monitor authentication, track data access, detect anomalies, and ensure compliance.

#### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Login Success Rate | Successful authentications | >99% | <95% |
| Failed Login Attempts | Consecutive failures per user | 0 | ≥5 |
| Privilege Changes | Grant/revoke operations | Audit | Any unplanned |
| Sensitive Data Access | Access to tagged sensitive data | Audit | Unusual patterns |
| Session Duration | Average session length | Baseline | >3x baseline |

#### Views

| View Name | Purpose |
|-----------|---------|
| `V_LOGIN_ACTIVITY` | Authentication event summary |
| `V_FAILED_LOGINS` | Failed authentication details |
| `V_DATA_ACCESS_PATTERNS` | Data access tracking |
| `V_PRIVILEGE_CHANGES` | Grant/revoke audit trail |
| `V_SESSION_ANALYSIS` | User session metrics |
| `V_USER_ROLE_MATRIX` | Role assignment tracking |

#### Security Event Classification

```
┌─────────────────────────────────────────────────────────────┐
│                   SECURITY EVENT SEVERITY                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   CRITICAL                           HIGH                    │
│   ────────                           ────                    │
│   • 5+ failed logins (same user)     • Privilege escalation  │
│   • Admin role changes               • New admin user        │
│   • Network policy violation         • Unusual access time   │
│                                                              │
│   MEDIUM                             LOW                     │
│   ──────                             ───                     │
│   • Failed login attempt             • Normal login          │
│   • New IP address                   • Standard query        │
│   • Off-hours access                 • Routine operations    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.6 Module 6: Metadata & Lineage Visibility

#### Purpose
Track data lineage, manage object dependencies, enable impact analysis, and ensure metadata completeness.

#### Capabilities

| Capability | Description |
|------------|-------------|
| Column-Level Lineage | Track data flow at column granularity |
| Object Dependencies | Map relationships between objects |
| Impact Analysis | Assess change impact before deployment |
| Tag Coverage | Monitor metadata/tag completeness |
| Catalog Management | Unified view of all data assets |

#### Views

| View Name | Purpose |
|-----------|---------|
| `V_OBJECT_DEPENDENCIES` | Object relationship mapping |
| `V_COLUMN_LINEAGE` | Column-level data flow tracking |
| `V_TAG_COVERAGE` | Tag assignment analysis |
| `V_OBJECT_CATALOG` | Unified object inventory |

#### Lineage Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA LINEAGE FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   SOURCE              TRANSFORM           CONSUME            │
│   ──────              ─────────           ───────            │
│                                                              │
│   ┌─────────┐        ┌─────────┐        ┌─────────┐         │
│   │ RAW     │───────▶│ STAGING │───────▶│  MART   │         │
│   │ TABLES  │        │  VIEWS  │        │ TABLES  │         │
│   └─────────┘        └─────────┘        └─────────┘         │
│        │                  │                  │               │
│        │                  │                  │               │
│        ▼                  ▼                  ▼               │
│   ┌─────────────────────────────────────────────────┐       │
│   │              ACCESS_HISTORY                      │       │
│   │  • Query ID, User, Timestamp                    │       │
│   │  • Direct Objects Accessed                      │       │
│   │  • Base Objects Accessed                        │       │
│   │  • Objects Modified                             │       │
│   │  • Columns Read/Written                         │       │
│   └─────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.7 Module 7: User & Workload Behavior Insights

#### Purpose
Analyze user behavior patterns, understand workload distribution, and enable capacity planning.

#### Key Metrics

| Metric | Description | Use Case |
|--------|-------------|----------|
| Activity Heatmap | Query volume by hour/day | Capacity planning |
| Query Type Distribution | Breakdown by operation type | Workload analysis |
| User Engagement Score | Composite activity metric | Adoption tracking |
| Concurrency Patterns | Simultaneous query analysis | Scaling decisions |
| Resource Consumption | Per-user/workload resource use | Chargeback |

#### Views

| View Name | Purpose |
|-----------|---------|
| `V_USER_ACTIVITY_HEATMAP` | Hourly activity patterns |
| `V_QUERY_TYPE_DISTRIBUTION` | Query operation breakdown |
| `V_WORKLOAD_BY_QUERY_TAG` | Tag-based workload analysis |
| `V_CONCURRENCY_ANALYSIS` | Peak concurrency tracking |
| `V_USER_ENGAGEMENT_SCORE` | User activity scoring |

#### Engagement Score Formula

```
Engagement_Score = 
    (Query_Count × 0.3) +
    (Active_Days × 2.0) +
    (Databases_Accessed × 1.5)
```

---

### 3.8 Module 8: Alerting & Automated Remediation

#### Purpose
Proactive issue detection, automated notifications, and self-healing capabilities.

#### Alert Configuration

| Alert Name | Trigger Condition | Severity | Schedule |
|------------|-------------------|----------|----------|
| `ALERT_LONG_RUNNING_QUERY` | Query > 10 minutes | HIGH | 5 min |
| `ALERT_FAILED_TASK` | Task failure detected | CRITICAL | 15 min |
| `ALERT_HIGH_CREDIT_USAGE` | Hourly credits > 10 | MEDIUM | 60 min |
| `ALERT_FAILED_LOGINS` | 5+ failed attempts | CRITICAL | 15 min |
| `ALERT_QUEUE_TIME_SPIKE` | Queue time > 60 sec | HIGH | 10 min |

#### Alert Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       ALERT WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │ CONDITION│───▶│  ALERT   │───▶│  ACTION  │             │
│   │  CHECK   │    │ TRIGGER  │    │ EXECUTE  │             │
│   └──────────┘    └──────────┘    └──────────┘             │
│        │               │               │                    │
│        │               │               │                    │
│        ▼               ▼               ▼                    │
│   ┌──────────────────────────────────────────────┐         │
│   │              T_ALERT_HISTORY                  │         │
│   │  • Alert ID, Name, Timestamp                 │         │
│   │  • Metric Value, Threshold                   │         │
│   │  • Status: TRIGGERED → ACKNOWLEDGED →        │         │
│   │            RESOLVED                          │         │
│   └──────────────────────────────────────────────┘         │
│                                                              │
│   NOTIFICATION CHANNELS:                                     │
│   ─────────────────────                                      │
│   • Email (via Notification Integration)                    │
│   • Slack/Teams (via Webhook)                               │
│   • PagerDuty (via API)                                     │
│   • Custom Endpoints                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.9 Module 9: Executive Dashboards & KPIs

#### Purpose
Provide high-level KPIs, SLA tracking, and strategic metrics for executive reporting.

#### Key Performance Indicators

| KPI | Description | Target | Weight |
|-----|-------------|--------|--------|
| Platform Health Score | Composite health metric | >95% | - |
| Query Success Rate | Successful query ratio | >99.5% | 40% |
| Task Success Rate | Successful task ratio | >99% | 30% |
| Login Success Rate | Authentication success | >99% | 20% |
| Queue Time Index | Inverse of avg queue time | >95% | 10% |

#### Views

| View Name | Purpose |
|-----------|---------|
| `V_PLATFORM_HEALTH_SCORE` | Real-time health calculation |
| `V_EXECUTIVE_SUMMARY` | Daily KPI snapshot |
| `V_WEEKLY_TRENDS` | Week-over-week analysis |
| `V_COST_EFFICIENCY` | Cost optimization metrics |
| `V_SLA_COMPLIANCE` | SLA target tracking |

#### Health Score Calculation

```
OVERALL_HEALTH_SCORE = 
    (Query_Success_Rate × 0.40) +
    (Task_Success_Rate × 0.30) +
    (Login_Success_Rate × 0.20) +
    (Queue_Performance_Index × 0.10)

Where:
    Queue_Performance_Index = MAX(0, 100 - (Avg_Queue_Sec × 2))
```

#### SLA Definitions

| SLA Type | Target | Measurement |
|----------|--------|-------------|
| Performance SLA | 95% queries < 60 sec | Query duration P95 |
| Availability SLA | 99.9% query success | Success rate |
| Queue SLA | 90% queries < 5 sec queue | Queue time P90 |

---

### 3.10 Module 10: Governance, Automation & Standardization

#### Purpose
Enforce governance policies, automate routine operations, and ensure platform standardization.

#### Governance Policies

| Policy | Category | Enforcement |
|--------|----------|-------------|
| Warehouse Auto-Suspend | COST | MANDATORY |
| Table Comments Required | METADATA | ADVISORY |
| Query Tag Usage | STANDARDIZATION | ADVISORY |
| Naming Conventions | STANDARDIZATION | MANDATORY |
| Role-Based Access | SECURITY | MANDATORY |

#### Automation Components

| Component | Schedule | Purpose |
|-----------|----------|---------|
| `TASK_WEEKLY_CLEANUP` | Sun 2AM | Purge old observability data |
| `TASK_DAILY_HEALTH_CHECK` | Daily 6AM | Log daily health scores |
| `SP_CLEANUP_OBSERVABILITY_DATA` | On-demand | Manual data cleanup |

#### Naming Convention Rules

```
Object Type     Pattern                    Example
───────────     ───────                    ───────
Database        [A-Z][A-Z0-9_]*           PROD_DW
Schema          [A-Z][A-Z0-9_]*           RAW_DATA
Table           [A-Z][A-Z0-9_]*           CUSTOMER_DIM
View            V_[A-Z][A-Z0-9_]*         V_SALES_SUMMARY
Procedure       SP_[A-Z][A-Z0-9_]*        SP_LOAD_DATA
Task            TASK_[A-Z][A-Z0-9_]*      TASK_DAILY_ETL
Alert           ALERT_[A-Z][A-Z0-9_]*     ALERT_HIGH_COST
```

---

## 4. Data Flow Architecture

### 4.1 Real-Time vs Batch Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA PROCESSING PATTERNS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   REAL-TIME (Latency: seconds)        NEAR-REAL-TIME (Latency: minutes)     │
│   ────────────────────────────        ─────────────────────────────────     │
│   • Information Schema queries        • Account Usage views                  │
│   • Current session metrics           • Alert checks (5-15 min)             │
│   • Active query monitoring           • Task status updates                  │
│                                                                              │
│   BATCH (Latency: hours)              SCHEDULED (Latency: defined)          │
│   ──────────────────────              ────────────────────────────          │
│   • Historical trend analysis         • Daily health reports                 │
│   • Cost aggregations                 • Weekly cleanup jobs                  │
│   • Storage metrics                   • Governance audits                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Retention Strategy

| Data Type | Hot Storage | Warm Storage | Archive |
|-----------|-------------|--------------|---------|
| Alert History | 7 days | 30 days | 90 days |
| Quality Results | 7 days | 30 days | 90 days |
| Audit Logs | 30 days | 90 days | 365 days |
| Account Usage | N/A (Snowflake managed) | 365 days | N/A |

---

## 5. Implementation Guide

### 5.1 Prerequisites

| Requirement | Details |
|-------------|---------|
| Snowflake Edition | Enterprise (recommended for DMF) |
| Role | ACCOUNTADMIN or equivalent |
| Warehouse | Dedicated observability warehouse |
| Database | Dedicated observability database |
| Permissions | IMPORTED PRIVILEGES on SNOWFLAKE database |

### 5.2 Deployment Steps

```
PHASE 1: Foundation (Day 1)
─────────────────────────────
□ Create dedicated warehouse (OBSERVABILITY_WH)
□ Create database and schema (OBSERVABILITY)
□ Grant necessary permissions
□ Deploy base views (Sections 1-7)

PHASE 2: Alerting (Day 2)
─────────────────────────────
□ Create alert configuration tables
□ Deploy alert definitions
□ Configure notification integrations
□ Resume and test alerts

PHASE 3: Automation (Day 3)
─────────────────────────────
□ Deploy stored procedures
□ Create scheduled tasks
□ Resume and verify tasks
□ Test cleanup procedures

PHASE 4: Governance (Day 4-5)
─────────────────────────────
□ Configure governance policies
□ Set up audit logging
□ Implement naming validations
□ Document and train teams

PHASE 5: Dashboards (Day 5-7)
─────────────────────────────
□ Build Snowsight dashboards
□ Configure refresh schedules
□ Set up executive reports
□ Enable self-service access
```

### 5.3 Post-Deployment Validation

```sql
-- Verify all objects created
SHOW VIEWS IN SCHEMA OBSERVABILITY;
SHOW TABLES IN SCHEMA OBSERVABILITY;
SHOW ALERTS IN SCHEMA OBSERVABILITY;
SHOW TASKS IN SCHEMA OBSERVABILITY;

-- Test key views return data
SELECT * FROM V_PLATFORM_HEALTH_SCORE;
SELECT * FROM V_EXECUTIVE_SUMMARY;
SELECT COUNT(*) FROM V_WAREHOUSE_PERFORMANCE_SUMMARY;

-- Verify alerts are active
SHOW ALERTS;
-- Look for STATE = 'started'
```

---

## 6. Security Considerations

### 6.1 Access Control Model

```
┌─────────────────────────────────────────────────────────────┐
│                    ROLE HIERARCHY                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ACCOUNTADMIN                              │
│                         │                                    │
│            ┌────────────┼────────────┐                      │
│            │            │            │                      │
│            ▼            ▼            ▼                      │
│     OBSERVABILITY  OBSERVABILITY  OBSERVABILITY            │
│       _ADMIN         _ANALYST       _VIEWER                │
│            │            │            │                      │
│            │            │            │                      │
│            ▼            ▼            ▼                      │
│     Full Access    Read + Write   Read Only                │
│     All Objects    Config Tables  Views Only               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Recommended Role Permissions

| Role | Permissions |
|------|-------------|
| OBSERVABILITY_ADMIN | Full CRUD on all objects, execute procedures, manage alerts |
| OBSERVABILITY_ANALYST | SELECT on all views, INSERT/UPDATE on config tables |
| OBSERVABILITY_VIEWER | SELECT on views only |

### 6.3 Data Sensitivity

| Data Category | Sensitivity | Access Control |
|---------------|-------------|----------------|
| Query Text | HIGH | Restricted to admins |
| User Names | MEDIUM | Role-based access |
| Credit Metrics | MEDIUM | FinOps team access |
| Login History | HIGH | Security team only |
| Access Patterns | HIGH | Audit team only |

---

## 7. Operations & Maintenance

### 7.1 Daily Operations

| Task | Frequency | Owner |
|------|-----------|-------|
| Review alert history | Daily | Platform Team |
| Check health score | Daily | Platform Team |
| Validate task execution | Daily | DataOps Team |
| Review failed queries | Daily | Platform Team |

### 7.2 Weekly Operations

| Task | Frequency | Owner |
|------|-----------|-------|
| Cost trend analysis | Weekly | FinOps Team |
| Security audit review | Weekly | Security Team |
| Governance compliance check | Weekly | Governance Team |
| Capacity planning review | Weekly | Platform Team |

### 7.3 Monthly Operations

| Task | Frequency | Owner |
|------|-----------|-------|
| Executive report generation | Monthly | Platform Team |
| SLA compliance review | Monthly | Management |
| Policy effectiveness review | Monthly | Governance Team |
| Framework enhancement planning | Monthly | Platform Team |

### 7.4 Troubleshooting Guide

| Issue | Possible Cause | Resolution |
|-------|----------------|------------|
| Views return no data | Account Usage latency | Wait 45 min - 3 hours |
| Alerts not firing | Alert suspended | `ALTER ALERT ... RESUME` |
| High observability costs | Too frequent queries | Optimize refresh schedules |
| Missing objects | Permissions issue | Grant IMPORTED PRIVILEGES |

---

## 8. Appendix

### 8.1 Object Reference

#### Views (28 total)

| Section | View Name |
|---------|-----------|
| 1 | V_WAREHOUSE_PERFORMANCE_SUMMARY |
| 1 | V_QUERY_PERFORMANCE_DISTRIBUTION |
| 1 | V_LONG_RUNNING_QUERIES |
| 1 | V_WAREHOUSE_SCALING_EVENTS |
| 1 | V_COMPILATION_EXECUTION_ANALYSIS |
| 2 | V_TASK_EXECUTION_SUMMARY |
| 2 | V_FAILED_TASKS_DETAIL |
| 2 | V_TABLE_FRESHNESS |
| 2 | V_COPY_HISTORY_SUMMARY |
| 2 | V_SNOWPIPE_PERFORMANCE |
| 3 | V_CREDIT_CONSUMPTION_WAREHOUSE |
| 3 | V_CREDIT_CONSUMPTION_USER |
| 3 | V_SERVERLESS_COSTS |
| 3 | V_STORAGE_USAGE_TRENDS |
| 3 | V_DATABASE_STORAGE_BREAKDOWN |
| 3 | V_COST_PER_QUERY |
| 3 | V_MONTHLY_COST_SUMMARY |
| 4 | V_SCHEMA_CHANGES |
| 4 | V_TABLE_STATISTICS |
| 5 | V_LOGIN_ACTIVITY |
| 5 | V_FAILED_LOGINS |
| 5 | V_DATA_ACCESS_PATTERNS |
| 5 | V_PRIVILEGE_CHANGES |
| 5 | V_SESSION_ANALYSIS |
| 5 | V_USER_ROLE_MATRIX |
| 6 | V_OBJECT_DEPENDENCIES |
| 6 | V_COLUMN_LINEAGE |
| 6 | V_TAG_COVERAGE |
| 6 | V_OBJECT_CATALOG |
| 7 | V_USER_ACTIVITY_HEATMAP |
| 7 | V_QUERY_TYPE_DISTRIBUTION |
| 7 | V_WORKLOAD_BY_QUERY_TAG |
| 7 | V_CONCURRENCY_ANALYSIS |
| 7 | V_USER_ENGAGEMENT_SCORE |
| 9 | V_PLATFORM_HEALTH_SCORE |
| 9 | V_EXECUTIVE_SUMMARY |
| 9 | V_WEEKLY_TRENDS |
| 9 | V_COST_EFFICIENCY |
| 9 | V_SLA_COMPLIANCE |
| 10 | V_NAMING_CONVENTION_COMPLIANCE |
| 10 | V_RESOURCE_GOVERNANCE |

### 8.2 Glossary

| Term | Definition |
|------|------------|
| Account Usage | Snowflake's built-in usage tracking schema |
| Credit | Snowflake's unit of compute consumption |
| DMF | Data Metric Function (Enterprise feature) |
| Health Score | Composite platform health metric |
| Lineage | Data flow tracking from source to consumption |
| Queue Time | Time queries wait before execution |
| SLA | Service Level Agreement |

### 8.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | March 2026 | Initial release |

---

*Document generated for Snowflake E2E Observability Framework*
*For questions or support, contact the Data Platform Team*
