# AI Usage Consumption Framework
## Design Documentation

**Version:** 1.0  
**Date:** March 16, 2026  
**Author:** Durga Prasad Katasani/CortexCode  
**Snowflake Account:** rpc07357  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Requirements](#2-business-requirements)
3. [Architecture Overview](#3-architecture-overview)
4. [Data Sources](#4-data-sources)
5. [Data Model](#5-data-model)
6. [Views Specification](#6-views-specification)
7. [Streamlit Dashboard](#7-streamlit-dashboard)
8. [Git Integration](#8-git-integration)
9. [Security & Access Control](#9-security--access-control)
10. [Operations & Maintenance](#10-operations--maintenance)
11. [Sample Queries](#11-sample-queries)
12. [Appendix](#12-appendix)

---

## 1. Executive Summary

### 1.1 Purpose

The AI Usage Consumption Framework provides comprehensive visibility into all AI and Machine Learning workloads running on the Snowflake account. It enables stakeholders to monitor, analyze, and optimize AI consumption across multiple dimensions including users, roles, warehouses, and models.

### 1.2 Scope

| In Scope | Out of Scope |
|----------|--------------|
| Cortex LLM Functions (COMPLETE, SUMMARIZE, TRANSLATE, etc.) | Third-party ML tools |
| Cortex Analyst (Text-to-SQL) | External API costs |
| Token consumption tracking | Non-AI compute costs |
| Credit attribution | Real-time streaming |
| User/Role/Warehouse analysis | Predictive forecasting |

### 1.3 Key Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| Executive Leadership | Total AI spend, ROI visibility |
| Finance | Cost allocation, chargeback |
| Data Engineering | Optimization opportunities |
| Data Science | Model usage patterns |
| Security | User access patterns |

### 1.4 Success Metrics

- **Visibility**: 100% coverage of AI workloads
- **Latency**: Dashboard refresh within 5 minutes
- **Accuracy**: Credit attribution within 0.01 credit variance
- **Adoption**: Executive team weekly usage

---

## 2. Business Requirements

### 2.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Track all Cortex LLM function usage | P0 |
| FR-02 | Track Cortex Analyst usage by user | P0 |
| FR-03 | Attribute consumption to users | P0 |
| FR-04 | Attribute consumption to roles | P1 |
| FR-05 | Attribute consumption to warehouses | P1 |
| FR-06 | Track token consumption by model | P0 |
| FR-07 | Provide daily/weekly/monthly trends | P0 |
| FR-08 | Support flexible time range filtering | P1 |
| FR-09 | Calculate week-over-week changes | P1 |
| FR-10 | Executive dashboard with KPIs | P0 |

### 2.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Query response time | < 5 seconds |
| NFR-02 | Data freshness | < 2 hours (ACCOUNT_USAGE latency) |
| NFR-03 | Historical retention | 365 days |
| NFR-04 | Concurrent users | 50+ |
| NFR-05 | Availability | 99.9% |

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SNOWFLAKE ACCOUNT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     DATA SOURCES (ACCOUNT_USAGE)                     │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  CORTEX_FUNCTIONS_    CORTEX_ANALYST_     QUERY_ATTRIBUTION_        │   │
│  │  USAGE_HISTORY        USAGE_HISTORY       HISTORY                   │   │
│  │                                                                     │   │
│  │  QUERY_HISTORY        WAREHOUSE_METERING_HISTORY                    │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              CONSUMPTION LAYER (AI_CONSUMPTION SCHEMA)               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│  │  │ CORTEX_FUNCTIONS │  │ CORTEX_ANALYST   │  │ AI_DAILY_SUMMARY │  │   │
│  │  │ _USAGE           │  │ _USAGE           │  │                  │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│  │  │ AI_USAGE_BY_USER │  │ AI_USAGE_BY_ROLE │  │ AI_USAGE_BY_     │  │   │
│  │  │                  │  │                  │  │ WAREHOUSE        │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│  │  │ TOKEN_ANALYSIS   │  │ SERVERLESS_AI_   │  │ AI_EXECUTIVE_    │  │   │
│  │  │                  │  │ USAGE            │  │ DASHBOARD        │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌──────────────────┐                                              │   │
│  │  │ AI_COST_TRENDS   │                                              │   │
│  │  └──────────────────┘                                              │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PRESENTATION LAYER                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │              AI_CONSUMPTION_DASHBOARD (Streamlit)             │  │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │   │
│  │  │  │  KPIs   │ │ Trends  │ │By User  │ │By Model │ │By WH    │ │  │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      VERSION CONTROL (Git)                           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  GIT_API_INTEGRATION  ──►  AI_DASHBOARD_REPO  ──►  Remote Git       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Overview

| Component | Type | Purpose |
|-----------|------|---------|
| `AI_CONSUMPTION` | Schema | Container for all framework objects |
| Views (10) | SQL Views | Analytical layers over ACCOUNT_USAGE |
| `AI_CONSUMPTION_DASHBOARD` | Streamlit App | Executive visualization |
| `AI_DASHBOARD_REPO` | Git Repository | Version control integration |
| `STREAMLIT_STAGE` | Stage | App file storage |

### 3.3 Data Flow

```
ACCOUNT_USAGE Tables (Source)
        │
        ▼
    SQL Views (Transform)
        │
        ▼
  Streamlit App (Present)
        │
        ▼
   Executive Users (Consume)
```

---

## 4. Data Sources

### 4.1 Primary Data Sources

#### 4.1.1 CORTEX_FUNCTIONS_USAGE_HISTORY

Tracks all Cortex LLM function invocations.

| Column | Type | Description |
|--------|------|-------------|
| `START_TIME` | TIMESTAMP_LTZ | Function execution start |
| `END_TIME` | TIMESTAMP_LTZ | Function execution end |
| `FUNCTION_NAME` | VARCHAR | Function name (COMPLETE, SUMMARIZE, etc.) |
| `MODEL_NAME` | VARCHAR | LLM model used (llama3.1-70b, etc.) |
| `WAREHOUSE_ID` | NUMBER | Warehouse identifier |
| `TOKEN_CREDITS` | NUMBER(38,9) | Credits consumed |
| `TOKENS` | NUMBER | Tokens processed |

**Latency**: ~2 hours  
**Retention**: 365 days

#### 4.1.2 CORTEX_ANALYST_USAGE_HISTORY

Tracks Cortex Analyst (Text-to-SQL) usage.

| Column | Type | Description |
|--------|------|-------------|
| `START_TIME` | TIMESTAMP_LTZ | Session start |
| `END_TIME` | TIMESTAMP_LTZ | Session end |
| `USERNAME` | VARCHAR | User who invoked Analyst |
| `CREDITS` | NUMBER(38,9) | Credits consumed |
| `REQUEST_COUNT` | NUMBER | Number of requests |

**Latency**: ~2 hours  
**Retention**: 365 days

#### 4.1.3 QUERY_ATTRIBUTION_HISTORY

Provides user and query attribution for credit consumption.

| Column | Type | Description |
|--------|------|-------------|
| `QUERY_ID` | VARCHAR | Unique query identifier |
| `WAREHOUSE_ID` | NUMBER | Warehouse identifier |
| `WAREHOUSE_NAME` | VARCHAR | Warehouse name |
| `USER_NAME` | VARCHAR | Executing user |
| `START_TIME` | TIMESTAMP_LTZ | Query start |
| `END_TIME` | TIMESTAMP_LTZ | Query end |
| `CREDITS_ATTRIBUTED_COMPUTE` | FLOAT | Attributed compute credits |

#### 4.1.4 QUERY_HISTORY

Provides role information for queries.

| Column | Type | Description |
|--------|------|-------------|
| `QUERY_ID` | VARCHAR | Unique query identifier |
| `ROLE_NAME` | VARCHAR | Role used for execution |
| `WAREHOUSE_ID` | NUMBER | Warehouse identifier |
| `START_TIME` | TIMESTAMP_LTZ | Query start |
| `END_TIME` | TIMESTAMP_LTZ | Query end |

#### 4.1.5 WAREHOUSE_METERING_HISTORY

Maps warehouse IDs to names.

| Column | Type | Description |
|--------|------|-------------|
| `WAREHOUSE_ID` | NUMBER | Warehouse identifier |
| `WAREHOUSE_NAME` | VARCHAR | Warehouse name |

### 4.2 Data Relationships

```
CORTEX_FUNCTIONS_USAGE_HISTORY
        │
        ├──── warehouse_id ────► WAREHOUSE_METERING_HISTORY
        │
        └──── warehouse_id ────► QUERY_ATTRIBUTION_HISTORY
              + time overlap          │
                                      └──── user_name
                                      
QUERY_HISTORY
        │
        └──── warehouse_id ────► CORTEX_FUNCTIONS_USAGE_HISTORY
              + time overlap          │
                                      └──── role_name
```

---

## 5. Data Model

### 5.1 Schema Design

**Database**: `SNOWFLAKE_LEARNING_DB`  
**Schema**: `AI_CONSUMPTION`

### 5.2 Object Inventory

| Object Name | Type | Description |
|-------------|------|-------------|
| `CORTEX_FUNCTIONS_USAGE` | View | Base Cortex functions data |
| `CORTEX_ANALYST_USAGE` | View | Base Cortex Analyst data |
| `AI_DAILY_SUMMARY` | View | Unified daily summary |
| `AI_USAGE_BY_USER` | View | User dimension analysis |
| `AI_USAGE_BY_ROLE` | View | Role dimension analysis |
| `AI_USAGE_BY_WAREHOUSE` | View | Warehouse dimension analysis |
| `TOKEN_ANALYSIS` | View | Token metrics deep-dive |
| `SERVERLESS_AI_USAGE` | View | Serverless consumption |
| `AI_EXECUTIVE_DASHBOARD` | View | Executive KPIs |
| `AI_COST_TRENDS` | View | WoW trend analysis |
| `STREAMLIT_STAGE` | Stage | Streamlit file storage |
| `AI_CONSUMPTION_DASHBOARD` | Streamlit | Executive dashboard |
| `GIT_SECRET` | Secret | Git authentication |
| `GIT_API_INTEGRATION` | API Integration | Git connectivity |
| `AI_DASHBOARD_REPO` | Git Repository | Source control |

### 5.3 Entity Relationship Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                        DIMENSION TABLES                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │    USER     │    │    ROLE     │    │  WAREHOUSE  │            │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤            │
│  │ user_name   │    │ role_name   │    │ warehouse_id│            │
│  │             │    │             │    │ warehouse_  │            │
│  │             │    │             │    │ name        │            │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘            │
│         │                  │                  │                    │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                         FACT TABLES                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  AI_DAILY_SUMMARY (Fact)                     │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │ usage_date    │ DATE       │ Date dimension                 │  │
│  │ service_type  │ VARCHAR    │ CORTEX_FUNCTIONS/ANALYST       │  │
│  │ service_name  │ VARCHAR    │ Function/Service name          │  │
│  │ model_name    │ VARCHAR    │ LLM model                      │  │
│  │ warehouse_id  │ NUMBER     │ FK to warehouse                │  │
│  │ total_tokens  │ NUMBER     │ Tokens consumed                │  │
│  │ total_credits │ NUMBER     │ Credits consumed               │  │
│  │ request_count │ NUMBER     │ Number of requests             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 6. Views Specification

### 6.1 CORTEX_FUNCTIONS_USAGE

**Purpose**: Base view for Cortex LLM function consumption.

**Grain**: One row per function invocation record.

**Lookback**: 365 days

```sql
CREATE OR REPLACE VIEW AI_CONSUMPTION.CORTEX_FUNCTIONS_USAGE AS
SELECT
    DATE(start_time) AS usage_date,
    HOUR(start_time) AS usage_hour,
    function_name,
    model_name,
    warehouse_id,
    tokens AS total_tokens,
    token_credits AS credits_used,
    start_time,
    end_time
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
WHERE start_time >= DATEADD('day', -365, CURRENT_DATE());
```

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `usage_hour` | NUMBER | Hour of usage (0-23) |
| `function_name` | VARCHAR | COMPLETE, SUMMARIZE, etc. |
| `model_name` | VARCHAR | LLM model name |
| `warehouse_id` | NUMBER | Warehouse identifier |
| `total_tokens` | NUMBER | Tokens processed |
| `credits_used` | NUMBER | Credits consumed |
| `start_time` | TIMESTAMP | Execution start |
| `end_time` | TIMESTAMP | Execution end |

---

### 6.2 CORTEX_ANALYST_USAGE

**Purpose**: Base view for Cortex Analyst consumption.

**Grain**: One row per usage record (hourly aggregates).

**Lookback**: 365 days

```sql
CREATE OR REPLACE VIEW AI_CONSUMPTION.CORTEX_ANALYST_USAGE AS
SELECT
    DATE(start_time) AS usage_date,
    HOUR(start_time) AS usage_hour,
    username AS user_name,
    credits,
    request_count,
    ROUND(credits / NULLIF(request_count, 0), 6) AS credits_per_request,
    start_time,
    end_time
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
WHERE start_time >= DATEADD('day', -365, CURRENT_DATE());
```

---

### 6.3 AI_DAILY_SUMMARY

**Purpose**: Unified daily summary across all AI services.

**Grain**: One row per date + service type + function + model + warehouse.

**Lookback**: 365 days

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `service_type` | VARCHAR | CORTEX_FUNCTIONS or CORTEX_ANALYST |
| `service_name` | VARCHAR | Function/service name |
| `model_name` | VARCHAR | LLM model (NULL for Analyst) |
| `warehouse_id` | NUMBER | Warehouse ID (NULL for Analyst) |
| `total_tokens` | NUMBER | Tokens processed |
| `total_credits` | NUMBER | Credits consumed |
| `request_count` | NUMBER | Number of invocations |

---

### 6.4 AI_USAGE_BY_USER

**Purpose**: User-level AI consumption attribution.

**Grain**: One row per user + service type + function + model.

**Lookback**: 90 days

**Attribution Method**: Join Cortex usage with Query Attribution on warehouse_id and overlapping time windows.

| Column | Type | Description |
|--------|------|-------------|
| `user_name` | VARCHAR | Snowflake username |
| `service_type` | VARCHAR | CORTEX_FUNCTIONS or CORTEX_ANALYST |
| `function_name` | VARCHAR | Function name |
| `model_name` | VARCHAR | LLM model |
| `total_tokens` | NUMBER | Tokens consumed |
| `total_credits` | NUMBER | Credits consumed |
| `invocation_count` | NUMBER | Number of invocations |

---

### 6.5 AI_USAGE_BY_ROLE

**Purpose**: Role-level AI consumption attribution.

**Grain**: One row per date + role + function + model.

**Lookback**: 90 days

**Attribution Method**: Join Cortex usage with Query History on warehouse_id and overlapping time windows to get role_name.

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `role_name` | VARCHAR | Snowflake role |
| `function_name` | VARCHAR | Function name |
| `model_name` | VARCHAR | LLM model |
| `total_tokens` | NUMBER | Tokens consumed |
| `total_credits` | NUMBER | Credits consumed |
| `query_count` | NUMBER | Number of queries |

---

### 6.6 AI_USAGE_BY_WAREHOUSE

**Purpose**: Warehouse-level AI consumption.

**Grain**: One row per date + warehouse + function + model.

**Lookback**: 90 days

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `warehouse_id` | NUMBER | Warehouse identifier |
| `warehouse_name` | VARCHAR | Warehouse name |
| `function_name` | VARCHAR | Function name |
| `model_name` | VARCHAR | LLM model |
| `total_tokens` | NUMBER | Tokens consumed |
| `total_credits` | NUMBER | Credits consumed |
| `invocation_count` | NUMBER | Number of invocations |

---

### 6.7 TOKEN_ANALYSIS

**Purpose**: Deep-dive into token consumption patterns by model.

**Grain**: One row per date + function + model + warehouse.

**Lookback**: 90 days

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `function_name` | VARCHAR | Function name |
| `model_name` | VARCHAR | LLM model |
| `warehouse_id` | NUMBER | Warehouse identifier |
| `warehouse_name` | VARCHAR | Warehouse name |
| `total_tokens` | NUMBER | Total tokens |
| `total_credits` | NUMBER | Total credits |
| `credits_per_million_tokens` | NUMBER | Cost efficiency metric |
| `invocation_count` | NUMBER | Invocation count |
| `avg_tokens_per_call` | NUMBER | Average tokens per call |
| `min_tokens` | NUMBER | Minimum tokens |
| `max_tokens` | NUMBER | Maximum tokens |

---

### 6.8 SERVERLESS_AI_USAGE

**Purpose**: Track serverless AI consumption (Cortex Analyst).

**Grain**: One row per date + service + context.

**Lookback**: 90 days

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date of usage |
| `serverless_service` | VARCHAR | Service name (CORTEX_ANALYST) |
| `context_info` | VARCHAR | Username or service context |
| `total_credits` | NUMBER | Credits consumed |
| `total_requests` | NUMBER | Request count |

---

### 6.9 AI_EXECUTIVE_DASHBOARD

**Purpose**: Executive KPI view with 30-day daily granularity.

**Grain**: One row per date (includes zero-usage days).

**Lookback**: 30 days

| Column | Type | Description |
|--------|------|-------------|
| `usage_date` | DATE | Date |
| `cortex_function_credits` | NUMBER | Cortex function credits |
| `cortex_function_tokens` | NUMBER | Cortex function tokens |
| `cortex_analyst_credits` | NUMBER | Cortex Analyst credits |
| `cortex_analyst_requests` | NUMBER | Cortex Analyst requests |
| `total_ai_credits` | NUMBER | Total AI credits |

---

### 6.10 AI_COST_TRENDS

**Purpose**: Week-over-week trend analysis.

**Grain**: One row per week.

**Lookback**: 12 weeks

| Column | Type | Description |
|--------|------|-------------|
| `week_start` | DATE | Week start date |
| `cortex_function_credits` | NUMBER | Weekly function credits |
| `cortex_analyst_credits` | NUMBER | Weekly Analyst credits |
| `total_ai_credits` | NUMBER | Total weekly credits |
| `prev_week_credits` | NUMBER | Previous week total |
| `wow_change_pct` | NUMBER | Week-over-week % change |

---

## 7. Streamlit Dashboard

### 7.1 Dashboard Overview

**Name**: `AI_CONSUMPTION_DASHBOARD`  
**Location**: `SNOWFLAKE_LEARNING_DB.AI_CONSUMPTION`  
**Warehouse**: `COMPUTE_WH`  
**Main File**: `ai_consumption_dashboard.py`

### 7.2 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔍 AI Consumption Dashboard                          [Time Range: ▼]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Total AI     │ │ Total        │ │ Total        │ │ Active       │   │
│  │ Credits      │ │ Tokens       │ │ Requests     │ │ Users        │   │
│  │   XX.XX      │ │  XXX,XXX     │ │   X,XXX      │ │     XX       │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  [Trends] [By User] [By Warehouse] [By Model] [By Function]            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Trend Visualization                          │   │
│  │                    (Stacked Area Chart)                         │   │
│  │                                                                 │   │
│  │     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                   │   │
│  │   ▓▓░░░░░░░░░░░░░░░░░░░░░░░▓▓▓                                 │   │
│  │ ▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓                              │   │
│  │ ────────────────────────────────────►                           │   │
│  │                   Date                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │   Daily Tokens              │  │   Cumulative Credits            │  │
│  │   (Bar Chart)               │  │   (Line Chart)                  │  │
│  └─────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Tab Specifications

| Tab | Visualizations | Data Source |
|-----|----------------|-------------|
| **Trends** | Stacked area (credits), Bar (tokens), Line (cumulative) | Inline queries |
| **By User** | Horizontal bar chart, Data table | Inline queries |
| **By Warehouse** | Horizontal bar chart, Summary table | Inline queries |
| **By Model** | Donut chart, Breakdown table | Inline queries |
| **By Function** | Horizontal bar chart, Function table | Inline queries |

### 7.4 Interactive Controls

| Control | Options | Default |
|---------|---------|---------|
| Time Range | 7, 14, 30, 90 days | 30 days |

### 7.5 Technical Specifications

| Aspect | Specification |
|--------|---------------|
| Framework | Streamlit in Snowflake |
| Charting | Altair |
| Data Caching | 5 minutes TTL |
| Session | `snowflake.snowpark.context.get_active_session()` |

---

## 8. Git Integration

### 8.1 Integration Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Local Git     │────►│  Remote Repo    │────►│   Snowflake     │
│   Repository    │     │  (GitHub/GitLab)│     │   Git Repo      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                       │
        │                        │                       │
        ▼                        ▼                       ▼
   Developer              Cloud Hosted            AI_DASHBOARD_REPO
   Workstation           Version Control         (Stage-like access)
```

### 8.2 Objects Required

| Object | Type | Purpose |
|--------|------|---------|
| `GIT_SECRET` | Secret | Store Git credentials (PAT) |
| `GIT_API_INTEGRATION` | API Integration | Authorize Git provider |
| `AI_DASHBOARD_REPO` | Git Repository | Sync with remote repo |

### 8.3 Setup Steps

1. **Create Personal Access Token** on Git provider
2. **Create Secret** with credentials
3. **Create API Integration** with allowed prefixes
4. **Create Git Repository** pointing to remote
5. **Fetch** to sync
6. **Update Streamlit** to use Git repo as root location

### 8.4 Sync Workflow

```
Developer pushes changes
         │
         ▼
Remote repository updated
         │
         ▼
ALTER GIT REPOSITORY ... FETCH
         │
         ▼
Snowflake Git Repo synced
         │
         ▼
Streamlit app reflects changes
```

---

## 9. Security & Access Control

### 9.1 Required Privileges

#### For Framework Setup (ACCOUNTADMIN)

| Privilege | Object | Purpose |
|-----------|--------|---------|
| CREATE SCHEMA | Database | Create AI_CONSUMPTION schema |
| CREATE VIEW | Schema | Create analytical views |
| CREATE STAGE | Schema | Create Streamlit stage |
| CREATE STREAMLIT | Schema | Create dashboard |
| CREATE SECRET | Schema | Git credentials |
| CREATE API INTEGRATION | Account | Git connectivity |
| CREATE GIT REPOSITORY | Schema | Git integration |

#### For Dashboard Usage

| Privilege | Object | Purpose |
|-----------|--------|---------|
| USAGE | Schema | Access AI_CONSUMPTION |
| SELECT | Views | Query analytical views |
| USAGE | Streamlit | Run dashboard |
| USAGE | Warehouse | Execute queries |

### 9.2 Recommended Role Structure

```sql
-- Create roles for the framework
CREATE ROLE IF NOT EXISTS AI_CONSUMPTION_ADMIN;
CREATE ROLE IF NOT EXISTS AI_CONSUMPTION_VIEWER;

-- Grant admin privileges
GRANT USAGE ON DATABASE SNOWFLAKE_LEARNING_DB TO ROLE AI_CONSUMPTION_ADMIN;
GRANT ALL ON SCHEMA AI_CONSUMPTION TO ROLE AI_CONSUMPTION_ADMIN;

-- Grant viewer privileges
GRANT USAGE ON DATABASE SNOWFLAKE_LEARNING_DB TO ROLE AI_CONSUMPTION_VIEWER;
GRANT USAGE ON SCHEMA AI_CONSUMPTION TO ROLE AI_CONSUMPTION_VIEWER;
GRANT SELECT ON ALL VIEWS IN SCHEMA AI_CONSUMPTION TO ROLE AI_CONSUMPTION_VIEWER;
GRANT USAGE ON STREAMLIT AI_CONSUMPTION_DASHBOARD TO ROLE AI_CONSUMPTION_VIEWER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE AI_CONSUMPTION_VIEWER;
```

### 9.3 Data Sensitivity

| Data Element | Sensitivity | Notes |
|--------------|-------------|-------|
| Username | Medium | PII - restrict as needed |
| Role name | Low | Organizational structure |
| Warehouse name | Low | Infrastructure info |
| Credits/Tokens | Low | Consumption metrics |
| Query content | N/A | Not captured in framework |

---

## 10. Operations & Maintenance

### 10.1 Monitoring

#### Health Check Query

```sql
-- Verify all views are accessible
SELECT 'CORTEX_FUNCTIONS_USAGE' AS view_name, COUNT(*) AS row_count 
FROM AI_CONSUMPTION.CORTEX_FUNCTIONS_USAGE
UNION ALL
SELECT 'CORTEX_ANALYST_USAGE', COUNT(*) 
FROM AI_CONSUMPTION.CORTEX_ANALYST_USAGE
UNION ALL
SELECT 'AI_DAILY_SUMMARY', COUNT(*) 
FROM AI_CONSUMPTION.AI_DAILY_SUMMARY;
```

#### Data Freshness Check

```sql
-- Check latest data timestamp
SELECT 
    'CORTEX_FUNCTIONS' AS source,
    MAX(start_time) AS latest_data,
    DATEDIFF('hour', MAX(start_time), CURRENT_TIMESTAMP()) AS hours_behind
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
UNION ALL
SELECT 
    'CORTEX_ANALYST',
    MAX(start_time),
    DATEDIFF('hour', MAX(start_time), CURRENT_TIMESTAMP())
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY;
```

### 10.2 Sync Git Repository

```sql
-- Run after pushing changes to Git
ALTER GIT REPOSITORY AI_CONSUMPTION.AI_DASHBOARD_REPO FETCH;

-- Verify sync
LIST @AI_CONSUMPTION.AI_DASHBOARD_REPO/branches/main/;
```

### 10.3 Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Empty results in views | No AI usage in time window | Verify AI features are being used |
| Dashboard not loading | Stage file missing | Upload file to stage |
| Git sync fails | Invalid credentials | Update GIT_SECRET with new PAT |
| Slow queries | Large data volume | Add date filters, use warehouse scaling |
| Missing user attribution | No query overlap | Expected - attribution is approximate |

### 10.4 Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Review dashboard metrics | Daily | Business Users |
| Verify data freshness | Weekly | Data Engineering |
| Git sync after code changes | As needed | Development |
| PAT rotation | 90 days | Security |
| Review access grants | Quarterly | Security |

---

## 11. Sample Queries

### 11.1 Executive Summary

```sql
-- Last 30 days total AI consumption
SELECT 
    SUM(total_ai_credits) AS total_credits,
    SUM(cortex_function_tokens) AS total_tokens,
    SUM(cortex_analyst_requests) AS analyst_requests
FROM AI_CONSUMPTION.AI_EXECUTIVE_DASHBOARD;
```

### 11.2 Top AI Users

```sql
-- Top 10 users by credit consumption
SELECT 
    user_name,
    service_type,
    ROUND(SUM(total_credits), 4) AS credits,
    SUM(invocation_count) AS invocations
FROM AI_CONSUMPTION.AI_USAGE_BY_USER
GROUP BY user_name, service_type
ORDER BY credits DESC
LIMIT 10;
```

### 11.3 Model Cost Efficiency

```sql
-- Cost per million tokens by model
SELECT 
    model_name,
    SUM(total_tokens) AS tokens,
    ROUND(SUM(total_credits), 4) AS credits,
    ROUND(SUM(total_credits) / NULLIF(SUM(total_tokens), 0) * 1000000, 4) AS cost_per_million
FROM AI_CONSUMPTION.TOKEN_ANALYSIS
GROUP BY model_name
ORDER BY cost_per_million DESC;
```

### 11.4 Week-over-Week Growth

```sql
-- Weekly trend with growth rate
SELECT 
    week_start,
    total_ai_credits,
    prev_week_credits,
    wow_change_pct
FROM AI_CONSUMPTION.AI_COST_TRENDS
ORDER BY week_start DESC;
```

### 11.5 Warehouse Utilization

```sql
-- AI consumption by warehouse
SELECT 
    warehouse_name,
    SUM(total_credits) AS total_credits,
    SUM(total_tokens) AS total_tokens,
    SUM(invocation_count) AS invocations
FROM AI_CONSUMPTION.AI_USAGE_BY_WAREHOUSE
GROUP BY warehouse_name
ORDER BY total_credits DESC;
```

---

## 12. Appendix

### 12.1 Complete Object DDL

All DDL statements are available in:
- `CoCo Explore.sql` - View definitions
- `git_integration_setup.sql` - Git integration setup
- `ai_consumption_dashboard.py` - Streamlit application

### 12.2 File Inventory

| File | Purpose |
|------|---------|
| `ai_consumption_dashboard.py` | Streamlit dashboard code |
| `git_integration_setup.sql` | Git integration DDL |
| `environment.yml` | Conda dependencies |
| `README.md` | Repository documentation |
| `.gitignore` | Git ignore rules |
| `AI_Consumption_Framework_Design.md` | This document |

### 12.3 Glossary

| Term | Definition |
|------|------------|
| **Cortex Functions** | Snowflake's LLM functions (COMPLETE, SUMMARIZE, TRANSLATE, etc.) |
| **Cortex Analyst** | Text-to-SQL capability using natural language |
| **Token** | Unit of text processing in LLM models |
| **Credit** | Snowflake billing unit for compute |
| **PAT** | Personal Access Token for Git authentication |
| **ACCOUNT_USAGE** | Snowflake schema with account-level metadata |

### 12.4 References

- [Snowflake Cortex LLM Functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- [Snowflake Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [ACCOUNT_USAGE Views](https://docs.snowflake.com/en/sql-reference/account-usage)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Git Integration](https://docs.snowflake.com/en/developer-guide/git/git-overview)

### 12.5 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-16 | Data Engineering | Initial release |

---

**Document End**

*Generated for SNOWFLAKE_LEARNING_DB.AI_CONSUMPTION framework*
