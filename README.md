# 🚚 Supply Chain Data Platform

> An end-to-end data engineering platform for ingesting, validating, transforming, warehousing, and analyzing supply chain data using Python, Apache Airflow, PostgreSQL, Docker, SQL, and Power BI.

---

## 📌 Project Overview

The **Supply Chain Data Platform** simulates a modern enterprise supply chain data environment.

The platform integrates operational CSV data and a simulated ERP system. Apache Airflow orchestrates the ETL workflow, including data ingestion, quality validation, transformation, and warehouse loading.

The transformed data is modeled using a **Star Schema** and stored in PostgreSQL. Power BI connects to the warehouse to provide interactive supply chain analytics.

### Data Flow

`Source Systems → Airflow → Data Quality → Transformations → PostgreSQL → Power BI`

---

## 🎯 Project Objectives

- Build an end-to-end data engineering pipeline
- Integrate CSV and ERP-style operational data
- Automate ETL workflows using Apache Airflow
- Implement automated data quality validation
- Transform raw data into fact and dimension tables
- Build a PostgreSQL analytical warehouse
- Implement Star Schema dimensional modeling
- Create SQL and DAX business metrics
- Connect the warehouse with Power BI
- Provide supply chain performance analytics

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation, ingestion, transformation |
| Apache Airflow | ETL orchestration |
| PostgreSQL | Data warehouse |
| Docker | Containerization |
| Power BI | Data visualization |
| Pandas | Data processing |
| NumPy | Numerical processing |
| Faker | Synthetic data generation |
| SQLite | ERP simulation |
| SQL | Analytics |
| YAML | Data quality configuration |
| Git/GitHub | Version control |

---

## 🏗️ Architecture

```text
┌─────────────────────────┐
│      DATA SOURCES       │
├─────────────────────────┤
│ CSV Operational Data    │
│ ERP / SAP Simulation    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      APACHE AIRFLOW     │
│   Workflow Orchestration│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      RAW DATA LAYER     │
│    CSV + ERP Extracts   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      DATA QUALITY       │
│ Nulls | Duplicates      │
│ Schema | Range Checks   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   TRANSFORMATION LAYER  │
│ Facts + Dimensions      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   POSTGRESQL WAREHOUSE  │
│       STAR SCHEMA       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        POWER BI         │
│ Supply Chain Analytics  │
└─────────────────────────┘
```

---

## 🔄 ETL Pipeline

The main Apache Airflow DAG is **`supply_chain_etl`**.

The pipeline consists of five major stages:
1. CSV Ingestion
2. ERP Ingestion
3. Data Quality Validation
4. Data Transformation
5. PostgreSQL Warehouse Loading

```text
CSV Ingestion ──────┐
                    │
ERP Ingestion ──────┤
                    ▼
              Data Quality
                    │
                    ▼
              Transformations
                    │
                    ▼
           PostgreSQL Warehouse
```

---

## 📂 Project Structure

```text
supply-chain-data-platform/
│
├── airflow/
│   └── dags/
│       ├── supply_chain_etl.py
│       └── supply_chain_test.py
│
├── ingestion/
│   ├── csv_ingestion.py
│   └── database_ingestion.py
│
├── transformations/
│   ├── dim_customer.py
│   ├── dim_date.py
│   ├── dim_product.py
│   ├── dim_supplier.py
│   ├── dim_warehouse.py
│   ├── fact_inventory.py
│   ├── fact_orders.py
│   ├── fact_purchase_orders.py
│   └── fact_shipments.py
│
├── quality/
│   ├── data_quality.py
│   └── inspect_data.py
│
├── warehouse/
│   └── load_warehouse.py
│
├── analytics/
│   └── sql/
│       └── supply_chain_kpi.sql
│
├── scripts/
├── config/
├── data/
├── powerbi/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📥 Data Sources

Synthetic data is used to simulate a real-world supply chain environment.

| Dataset | Records |
|---|---|
| Suppliers | 100 |
| Products | 1,000 |
| Warehouses | 10 |
| Customers | 10,000 |
| Inventory | 1,000 |
| Orders | 100,000 |
| Shipments | 59,953 |
| Purchase Orders | 10,000 |

* The ERP source is simulated using SQLite and contains supplier, product, warehouse, and purchase-order data.
* This project uses a simulated ERP/SAP source rather than a live SAP system.

---

## 🧪 Data Quality

Automated data quality validation is performed before transformation.

**Validation Checks:**
- Required columns
- Null values
- Duplicate records
- Numeric ranges
- Dataset-specific validation rules

```text
                    Raw Data
                       │
                       ▼
                Data Quality
                   Checks
                       │
              ┌────────┴────────┐
              │                 │
            PASS              FAIL
              │                 │
              ▼                 ▼
       Transformation       Pipeline Stops
```

If a quality check fails, the Airflow task raises an error and prevents invalid data from moving downstream.

---

## ⭐ Data Warehouse

The PostgreSQL warehouse follows a **Star Schema** design.

### Dimension Tables
- `dim_supplier`
- `dim_product`
- `dim_warehouse`
- `dim_customer`
- `dim_date`

### Fact Tables
- `fact_orders`
- `fact_inventory`
- `fact_shipments`
- `fact_purchase_orders`

### Why Star Schema?
The Star Schema separates:
- **Fact tables** → measurable business events and numerical metrics
- **Dimension tables** → descriptive business context and attributes

This design optimizes query performance, simplifies joins, and enables fast aggregations in Power BI.

---

## 📊 Business Analytics

The platform supports analytics across multiple supply chain domains:

- **💰 Sales:** Total sales, total orders, units sold, and sales by product category.
- **📦 Inventory:** Total inventory value, low-stock alerts, and stockout risk assessment.
- **🚚 Shipments:** Total shipments, on-time vs. delayed shipments, on-time delivery rate (OTD %), and carrier performance.
- **🏭 Warehouses:** Order distribution by facility and warehouse throughput comparisons.
- **🛒 Procurement:** Purchase order volume, total PO spend, and supplier fulfillment lead times.

---

## 📈 Power BI

Power BI connects directly to the PostgreSQL analytical warehouse.

**Dashboard Coverage:**
- Total Sales, Orders, and Units Sold
- On-Time Delivery % & Delayed Shipments
- Low Stock Alerts & Inventory Valuation
- Total PO Spend & Supplier Delivery Scorecards
- Warehouse Throughput & Order Distribution

**Interactive Slicers:**
- Date Range
- Product Category

---

## 🔑 Key DAX Measures

```text
Total Sales
Total Orders
Total Units Sold
Total Shipments
Delayed Shipments
On-Time Delivery %
Low Stock Products
Total Inventory Value
Total PO Value
```

---

## 🗄️ PostgreSQL Analytics

The warehouse contains embedded SQL analytical logic. A consolidated KPI view is implemented as **`supply_chain_kpi`**, providing metrics such as:
- Total orders & sales revenue
- Low-stock inventory alerts
- Total, on-time, and delayed shipments
- On-time delivery percentage
- Cumulative logistics & shipping costs
- Purchase order volume and spend

---

## ⚙️ Warehouse Loading

The PostgreSQL loader supports:
- Automated table creation with primary and foreign key constraints
- Idempotent and rerunnable warehouse loads
- Target table truncation before pipeline reload
- Chunked loading for high-volume fact tables to optimize memory consumption
- Post-load row-count and integrity validation

---

## 🚀 Running the Project

### 1. Clone the Repository
```bash
git clone [https://github.com/Charan304304/supply-chain-data-platform.git](https://github.com/Charan304304/supply-chain-data-platform.git)
cd supply-chain-data-platform
```

### 2. Create Python Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Generate Sample Data
```powershell
python scripts/generate_data.py
```

### 5. Create ERP Database
```powershell
python scripts/create_erp_database.py
```

### 6. Start Airflow and PostgreSQL
```powershell
cd airflow
docker compose up -d
```

- **Airflow Web UI:** [http://localhost:8081](http://localhost:8081)
- **PostgreSQL Connection:**
  - **Host:** `localhost:5432`
  - **Database:** `supply_chain_warehouse`

### 7. Run the Airflow Pipeline
Trigger and monitor the **`supply_chain_etl`** DAG directly within the Airflow Web UI.

---

## 🔐 Security & Version Control

The project uses `.gitignore` to prevent sensitive credentials and intermediate pipeline artifacts from being committed:

```text
.env
.venv/
airflow/logs/
__pycache__/
*.pyc
*.db
data/raw/
data/processed/
data/quality_reports/
```

---

## 💡 Engineering Concepts Demonstrated

- End-to-End Orchestrated ETL Pipelines
- Apache Airflow DAG Authoring & Dependency Management
- Automated Data Quality Gates
- Simulated ERP/Database Integration
- Star Schema Dimensional Modeling
- PostgreSQL Analytical Warehousing
- Chunked Data Ingestion & Memory Management
- SQL KPI Views & DAX Metric Design
- Containerization with Docker Compose
- Power BI Business Intelligence Reporting

---

## 🚀 Future Enhancements

- Live SAP/ERP connector integration
- Incremental loads via Change Data Capture (CDC)
- Slowly Changing Dimensions (SCD Type 2) implementation
- Transformation orchestration via dbt
- CI/CD workflow automation using GitHub Actions
- Cloud Data Lakehouse migration (Databricks / Snowflake / Microsoft Fabric)
- Real-time streaming ingestion for inventory updates

---

## 👨‍💻 Author

**Charan Simhadri**  
*Aspiring Data Engineer*  
`Python` · `SQL` · `Apache Airflow` · `PostgreSQL` · `Docker` · `Power BI` · `Pandas` · `ETL` · `Data Warehousing`

⭐ *If you find this project useful, consider giving the repository a star!*
