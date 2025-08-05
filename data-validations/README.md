<!--
---
title: "Phase 1: Data Integrity"
description: "Database schema design and foundational validation for DESI cosmic void galaxy analysis, establishing PostgreSQL infrastructure for 6.4M galaxy records"
author: "VintageDon - https://github.com/vintagedon"
ai_contributor: "Claude Sonnet 4"
date: "2025-08-05"
version: "1.0"
status: "Published"
tags:
- type: [directory-overview/phase-documentation/database-schema]
- domain: [postgresql/database-design/data-integrity]
- tech: [postgresql/sql/dbml]
- phase: [phase-1]
related_documents:
- "[Data Validations Overview](../README.md)"
- "[Phase 2: Physical Plausibility](../phase-2-physical-plausibility/README.md)"
---
-->

# 🗄️ **Phase 1: Data Integrity**

Database schema design and foundational validation for DESI cosmic void galaxy analysis, establishing the PostgreSQL infrastructure for managing 6.4 million galaxy records from FastSpecFit and cosmic void catalogs from DESIVAST. This phase provides the structural foundation ensuring data integrity and relational consistency before scientific analysis.

## **Overview**

Phase 1 represents the foundational database infrastructure layer of the DESI cosmic void galaxy analysis pipeline. This phase transforms distributed FITS catalog data into a centralized, query-optimized PostgreSQL database architecture implementing enterprise-grade schemas for astronomical data management.

The phase establishes dual-database architecture separating galaxy properties (`desi_void_fastspecfit`) from cosmic void catalogs (`desi_void_desivast`) while maintaining efficient cross-referencing capabilities. All schema designs are documented using DBML (Database Markup Language) and deployed through systematic SQL scripts ensuring reproducible infrastructure deployment.

---

## **📂 Directory Contents**

This section provides systematic navigation to all Phase 1 database schema and validation components.

### **Schema Definition Files**

| **File** | **Purpose** | **Link** |
|----------|-------------|----------|
| **[desi_void_fastspecfit.sql](desi_void_fastspecfit.sql)** | PostgreSQL schema for FastSpecFit galaxy properties database | [desi_void_fastspecfit.sql](desi_void_fastspecfit.sql) |
| **[desi_void_desivast.sql](desi_void_desivast.sql)** | PostgreSQL schema for DESIVAST cosmic void catalogs database | [desi_void_desivast.sql](desi_void_desivast.sql) |

### **Documentation Files**

| **File** | **Purpose** | **Link** |
|----------|-------------|----------|
| **[fastspecfit.dbml](fastspecfit.dbml)** | DBML documentation for FastSpecFit galaxy properties schema | [fastspecfit.dbml](fastspecfit.dbml) |
| **[desivast.dbml](desivast.dbml)** | DBML documentation for DESIVAST void catalogs schema | [desivast.dbml](desivast.dbml) |
| **[phase-1-validation-summary.md](phase-1-validation-summary.md)** | Complete validation log from successful Phase 1 integrity testing | [phase-1-validation-summary.md](phase-1-validation-summary.md) |

---

## **📁 Repository Structure**

``` markdown
phase-1-data-integrity/
├── 🗄️ desi_void_fastspecfit.sql    # FastSpecFit galaxy properties schema
├── 🗄️ desi_void_desivast.sql       # DESIVAST void catalogs schema
├── 📋 fastspecfit.dbml              # FastSpecFit schema documentation
├── 📋 desivast.dbml                 # DESIVAST schema documentation
├── 📊 phase-1-validation-summary.md # Validation execution log
└── 📝 README.md                     # This file
```

### **Navigation Guide:**

- **[🗄️ FastSpecFit Schema](desi_void_fastspecfit.sql)** - Complete PostgreSQL schema for 6.4M galaxy properties
- **[🗄️ DESIVAST Schema](desi_void_desivast.sql)** - Multi-algorithm cosmic void catalog database schema
- **[📋 Schema Documentation](fastspecfit.dbml)** - DBML documentation viewable at dbdocs.io
- **[📊 Validation Results](phase-1-validation-summary.md)** - Successful integrity validation execution log

---

## **🔗 Related Categories**

This section establishes horizontal relationships within the data validations knowledge graph.

| **Category** | **Relationship** | **Documentation** |
|--------------|------------------|-------------------|
| **[Phase 2: Physical Plausibility](../phase-2-physical-plausibility/README.md)** | **Depends-on** - Requires Phase 1 database infrastructure | [../phase-2-physical-plausibility/README.md](../phase-2-physical-plausibility/README.md) |
| **[Database Infrastructure](../../infrastructure/database/README.md)** | **Integrates-with** - Deployed on proj-pgsql01 PostgreSQL server | [../../infrastructure/database/README.md](../../infrastructure/database/README.md) |
| **[DESI Cosmic Void Project](../../astronomy-projects/desi-cosmic-void-galaxies/README.md)** | **Provides-to** - Database foundation for scientific analysis | [../../astronomy-projects/desi-cosmic-void-galaxies/README.md](../../astronomy-projects/desi-cosmic-void-galaxies/README.md) |

---

## **Getting Started**

For new users approaching Phase 1 database schemas:

1. **Start Here:** [DBML Documentation](https://dbdocs.io/crainbramp/desi_void_fastspecfit) - Visual schema browser for FastSpecFit database
2. **Schema Deployment:** [desi_void_fastspecfit.sql](desi_void_fastspecfit.sql) - Complete SQL schema for galaxy properties database
3. **Validation Reference:** [phase-1-validation-summary.md](phase-1-validation-summary.md) - Successful validation execution demonstrating schema integrity
4. **Next Phase:** [Phase 2: Physical Plausibility](../phase-2-physical-plausibility/README.md) - Scientific parameter validation building on Phase 1 foundation

---

## **Database Architecture Summary**

### **FastSpecFit Galaxy Properties Database**

**Purpose:** Central repository for 6.4 million galaxy physical properties derived from DESI FastSpecFit catalog  
**Key Table:** `fastspecfit_galaxies` with TARGETID primary key  
**Documentation:** [dbdocs.io/crainbramp/desi_void_fastspecfit](https://dbdocs.io/crainbramp/desi_void_fastspecfit)

**Core Columns:**

- `targetid` (BIGINT) - Unique DESI target identifier
- `ra`, `dec` (DOUBLE PRECISION) - Celestial coordinates
- `z` (DOUBLE PRECISION) - Redshift measurements
- `logmstar`, `sfr` (REAL) - Stellar mass and star formation rate
- `healpix_id`, `source_file` - Data provenance tracking

### **DESIVAST Cosmic Void Database**

**Purpose:** Multi-algorithm cosmic void catalog supporting systematic uncertainty analysis  
**Key Tables:** Algorithm-specific void catalogs plus unified `desivast_voids` table  
**Documentation:** [dbdocs.io/crainbramp/desi_void_desivast](https://dbdocs.io/crainbramp/desi_void_desivast)

**Algorithm Support:**

- `desivast_revolver_voids` - REVOLVER algorithm results
- `desivast_vide_voids` - VIDE algorithm results  
- `desivast_zobov_voids` - ZOBOV algorithm results
- `desivast_voidfinder_maximals` - VoidFinder maximal voids
- `desivast_voids` - Unified catalog across all algorithms

### **Validation Status**

**Integrity Validation:** ✅ **PASSED** - All 22 validation checks successful  
**Schema Compliance:** ✅ **VERIFIED** - Complete referential integrity  
**Data Completeness:** ✅ **CONFIRMED** - No NULL values in critical scientific parameters  
**Performance Ready:** ✅ **OPTIMIZED** - Indexed for spatial cross-matching queries

---

## **Document Information**

| **Field** | **Value** |
|-----------|-----------|
| **Author** | VintageDon - <https://github.com/vintagedon> |
| **Created** | 2025-08-05 |
| **Last Updated** | 2025-08-05 |
| **Version** | 1.0 |

---
Tags: phase-1, database-schema, postgresql, data-integrity, fastspecfit, desivast
