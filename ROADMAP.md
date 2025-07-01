# 🗺️ **DESI Cosmic Voids Implementation Roadmap**

This roadmap outlines the complete technical implementation plan for analyzing galaxy properties within cosmic voids using DESI DR1 data. It provides a systematic approach from environment setup through final scientific analysis and publication.

## 📋 **Project Overview**

**Scientific Objective:** Perform definitive measurement of large-scale cosmic environment influence on galaxy evolution by quantifying how stellar mass and star formation rate differ for galaxies in cosmic voids compared to surrounding "walls."

**Data Scale:** 27.6GB total download

- **DESIVAST Void Catalogs:** ~1.2GB (8 files across NGC/SGC hemispheres)
- **FastSpecFit Galaxy Properties:** ~26.4GB (12 HEALPix-distributed files)

**Infrastructure Requirements:**

- **Database Server:** proj-pg01 (8 vCPU, 48GB RAM, 250GB NVMe storage)
- **Analysis Platform:** proj-dp01 (4 vCPU, 16GB RAM, 100GB NVMe storage)
- **Backup Infrastructure:** pbs01 with 4TB Samsung 990 Pro storage

---

## 🎯 **Phase 1: Project Setup & Environment (1 Week)**

### **Objective**

Configure robust and reproducible Python environment with all necessary libraries for data handling, database interaction, analysis, and visualization.

### **Key Dependencies**

- **astropy:** Core astronomy package for FITS files and coordinate handling
- **pandas:** High-performance data structures and analysis tools
- **numpy:** Fundamental scientific computing package
- **sqlalchemy:** SQL toolkit and Object-Relational Mapper
- **psycopg2-binary:** PostgreSQL adapter for Python
- **matplotlib & seaborn:** Visualization libraries for publication-quality plots
- **scipy:** Statistical analysis and scientific computing

### **Environment Setup**

```bash
# Create virtual environment
python3 -m venv desi_void_env
source desi_void_env/bin/activate

# Install required packages
pip install astropy pandas numpy sqlalchemy psycopg2-binary matplotlib seaborn scipy
```

### **Deliverables**

- ✅ Configured Python virtual environment
- ✅ Validated library installations
- ✅ Environment documentation and requirements.txt

---

## 🗄️ **Phase 2: Database Architecture & Initialization (1 Week)**

### **Objective**

Design and create PostgreSQL database schema to efficiently store and query DESI DR1 catalogs, following successful strategies from large astronomical surveys.

### **Database Design**

- **Database Name:** `desi_dr1_db`
- **Schema Organization:**
  - `raw_catalogs`: Pristine data as ingested from FITS files (read-only after ingestion)
  - `science_analysis`: Derived tables, cross-matched catalogs, and analysis products

### **Core Table Structures**

#### **FastSpecFit Galaxy Properties**

```sql
CREATE TABLE raw_catalogs.fastspec_iron (
    TARGETID BIGINT PRIMARY KEY,
    RA DOUBLE PRECISION,
    DEC DOUBLE PRECISION,
    Z DOUBLE PRECISION,
    LOGMSTAR REAL,
    SFR REAL,
    VDISP REAL,
    AGE REAL,
    AV REAL,
    DN4000 REAL,
    OII_3727_FLUX REAL,
    HALPHA_FLUX REAL
);
```

#### **DESIVAST Void Catalog**

```sql
CREATE TABLE raw_catalogs.desivast_voids (
    VOID_ID SERIAL PRIMARY KEY,
    VOID_NAME VARCHAR(255) UNIQUE,
    RA DOUBLE PRECISION,
    DEC DOUBLE PRECISION,
    Z REAL,
    EFFECTIVE_RADIUS REAL,
    ALGORITHM VARCHAR(50) -- 'VoidFinder', 'V2_REVOLVER', 'V2_VIDE'
);
```

#### **Void Membership Linking**

```sql
CREATE TABLE raw_catalogs.desivast_void_members (
    MEMBER_ID SERIAL PRIMARY KEY,
    VOID_NAME VARCHAR(255) REFERENCES raw_catalogs.desivast_voids(VOID_NAME),
    TARGETID BIGINT REFERENCES raw_catalogs.fastspec_iron(TARGETID),
    IS_INTERIOR_GALAXY BOOLEAN
);
```

### **Spatial Indexing**

```sql
-- Q3C spatial indexing for astronomical coordinates
CREATE INDEX ON raw_catalogs.fastspec_iron (q3c_ang2ipix(ra, dec));
```

### **Deliverables**

- ✅ PostgreSQL 16 database with optimized configuration
- ✅ Complete schema design with proper indexing
- ✅ Database documentation and setup scripts

---

## 📥 **Phase 3: Data Ingestion Pipeline (1 Week)**

### **Objective**

Develop Python pipeline to download, read, and insert FastSpecFit and DESIVAST catalog data into PostgreSQL database.

### **Data Sources**

#### **DESIVAST Void Catalogs**

- **Source:** <https://data.desi.lbl.gov/public/dr1/vac/dr1/desivast/v1.0/>
- **Files:** 8 total (VoidFinder, V2_REVOLVER, V2_VIDE algorithms × NGC/SGC hemispheres)
- **Size:** ~1.2GB total

#### **FastSpecFit Galaxy Properties**

- **Source:** <https://data.desi.lbl.gov/public/dr1/vac/dr1/fastspecfit/iron/v3.0/catalogs/>
- **Files:** 12 HEALPix-distributed files (fastspec-iron-main-bright-nside1-hp*.fits)
- **Size:** ~26.4GB total

### **Ingestion Pipeline Architecture**

```python
# Core ingestion workflow
def ingest_fastspec_data(db_engine):
    """Process FastSpecFit FITS files and load into database"""
    fits_files = glob.glob(os.path.join(FASTSPEC_DIR, 'fastspec-*.fits.gz'))
    
    for f_path in fits_files:
        with fits.open(f_path) as hdul:
            data = hdul['FASTSPEC'].data
            df = pd.DataFrame({col.lower(): data[col] for col in columns_to_keep})
            df.to_sql('fastspec_iron', db_engine, schema='raw_catalogs', 
                     if_exists='append', index=False, chunksize=10000)

def ingest_desivast_data(db_engine):
    """Process DESIVAST void catalogs and member lists"""
    algorithms = ['VoidFinder', 'V2_REVOLVER', 'V2_VIDE']
    
    for algo in algorithms:
        # Process void properties and member lists
        # Handle NGC/SGC hemisphere files
        # Load with proper algorithm tagging
```

### **Data Validation**

- Record counts and data integrity checks
- Coordinate range validation
- Cross-reference validation between tables
- Statistical summaries and data quality metrics

### **Deliverables**

- ✅ Complete data ingestion pipeline
- ✅ 27.6GB DESI DR1 data loaded into PostgreSQL
- ✅ Data validation and quality assessment reports

---

## 🔬 **Phase 4: Scientific Workflow & Analysis Pipeline (2 Weeks)**

### **Objective**

Create reproducible workflow to define void and control samples, extract their properties, and perform statistical comparisons.

### **Unified Science Table Creation**

```sql
CREATE TABLE science_analysis.galaxy_sample_full AS
SELECT
    fsf.targetid,
    fsf.ra, fsf.dec, fsf.z,
    fsf.logmstar, fsf.sfr,
    (fsf.sfr / POWER(10, fsf.logmstar)) AS ssfr,
    vm.void_name,
    v.algorithm,
    vm.is_interior_galaxy
FROM raw_catalogs.fastspec_iron AS fsf
LEFT JOIN raw_catalogs.desivast_void_members AS vm ON fsf.targetid = vm.targetid
LEFT JOIN raw_catalogs.desivast_voids AS v ON vm.void_name = v.void_name;
```

### **Environmental Classification Algorithm**

```python
def classify_galaxy_environment(galaxy_coords, void_catalog):
    """
    3D spatial classification of galaxies relative to void boundaries
    
    Process:
    1. Calculate comoving distance from galaxy to each void center
    2. Compare distance to void effective radius
    3. Classify as 'Void' if inside any void, 'Wall' otherwise
    """
    for galaxy in galaxy_sample:
        distances = calculate_comoving_distances(galaxy, void_centers)
        inside_void = any(dist < void_radius for dist, void_radius in zip(distances, void_radii))
        galaxy.environment = 'Void' if inside_void else 'Wall'
```

### **Statistical Analysis Framework**

#### **1. Galaxy Stellar Mass Function (GSMF)**

- **Method:** Number density vs. stellar mass for void and wall populations
- **Significance:** Fundamental probe of environment effects on galaxy assembly
- **Output:** Mass-dependent environmental effects quantification

#### **2. Star-Forming Main Sequence Analysis**

- **Method:** SFR vs. stellar mass correlation by environment
- **Significance:** Direct probe of environmental effects on star formation efficiency
- **Output:** Environmental shifts in star formation relationships

#### **3. Quenched Fraction Measurements**

- **Method:** Fraction of galaxies below SFR threshold by mass bins and environment
- **Significance:** Quantitative measurement of environmental quenching efficiency
- **Output:** Environment-dependent quenching mechanisms

### **Statistical Validation**

```python
def analyze_samples(void_df, control_df):
    """Kolmogorov-Smirnov test for distribution differences"""
    ks_statistic, p_value = stats.ks_2samp(void_df['log_ssfr'], control_df['log_ssfr'])
    
    if p_value < 0.05:
        print("Significant environmental effect detected")
    else:
        print("No significant environmental difference")
```

### **Deliverables**

- ✅ Environmental classification for all galaxies
- ✅ Statistical analysis results with significance testing
- ✅ Comparative population studies across void algorithms

---

## 📊 **Phase 5: Visualization & Interpretation (1 Week)**

### **Objective**

Create publication-quality plots comparing properties of void and control galaxies.

### **Key Visualizations**

#### **1. sSFR Distribution Comparison**

```python
def plot_ssfr_distribution(void_df, control_df, algorithm):
    plt.figure(figsize=(10, 6))
    sns.kdeplot(void_df['log_ssfr'], label='Void Galaxies', fill=True, alpha=0.5)
    sns.kdeplot(control_df['log_ssfr'], label='Wall Galaxies', fill=True, alpha=0.5)
    plt.title(f'Specific Star Formation Rate Distribution ({algorithm} Voids)')
    plt.xlabel('log(sSFR / yr⁻¹)')
    plt.ylabel('Density')
```

#### **2. Star Formation Main Sequence**

```python
def plot_main_sequence(void_df, control_df, algorithm):
    plt.figure(figsize=(10, 8))
    plt.hexbin(control_df['logmstar'], np.log10(control_df['sfr'] + 1e-3),
               gridsize=100, cmap='Reds', alpha=0.6, label='Wall')
    plt.hexbin(void_df['logmstar'], np.log10(void_df['sfr'] + 1e-3),
               gridsize=100, cmap='Blues', alpha=0.6, label='Void')
    plt.xlabel('log(Stellar Mass / M☉)')
    plt.ylabel('log(Star Formation Rate / M☉ yr⁻¹)')
```

#### **3. Quenched Fraction Analysis**

- Mass-binned quenched fraction comparison
- Environment-dependent trends
- Statistical significance assessment

### **Deliverables**

- ✅ Publication-quality figures for all three void algorithms
- ✅ Statistical significance documentation
- ✅ Environmental effect quantification

---

## 📝 **Phase 6: Manuscript Preparation (3 Weeks)**

### **Objective**

Write comprehensive scientific paper documenting methodology, results, and implications for galaxy evolution theory.

### **Paper Structure**

1. **Abstract:** Precision environmental constraints summary
2. **Introduction:** Galaxy evolution and environmental context
3. **Data & Methods:** DESI DR1, DESIVAST, environmental classification
4. **Results:** GSMF, main sequence, quenched fraction analysis
5. **Discussion:** Theoretical implications and simulation comparison
6. **Conclusions:** Environmental quenching constraints and future work

### **Key Results Documentation**

- Quantitative environmental effect measurements
- Statistical significance across void algorithms
- Comparison with theoretical predictions
- Implications for galaxy evolution models

### **Deliverables**

- ✅ Complete manuscript draft
- ✅ Publication-quality figures and tables
- ✅ Supplementary material and data products

---

## 🔄 **Phase 7: Internal Review & Submission (2 Weeks)**

### **Objective**

Circulate draft among collaborators for feedback, revise, and submit to peer-reviewed journal.

### **Review Process**

- Internal technical review and validation
- Scientific methodology verification
- Statistical analysis validation
- Figure quality and clarity assessment

### **Target Journals**

- **Primary:** The Astrophysical Journal
- **Alternative:** Monthly Notices of the Royal Astronomical Society
- **Considerations:** Impact factor, review timeline, open access policies

### **Deliverables**

- ✅ Peer-reviewed manuscript submission
- ✅ Supplementary data products
- ✅ Public value-added catalog release

---

## 📅 **Timeline Summary**

| **Phase** | **Duration** | **Key Deliverable** | **Dependencies** |
|-----------|--------------|-------------------|------------------|
| **1. Environment Setup** | 1 Week | Configured Python environment | Hardware deployment |
| **2. Database Architecture** | 1 Week | PostgreSQL schema and optimization | Phase 1 completion |
| **3. Data Ingestion** | 1 Week | 27.6GB DESI data loaded | Phases 1-2 completion |
| **4. Scientific Analysis** | 2 Weeks | Environmental classification and statistics | Phase 3 completion |
| **5. Visualization** | 1 Week | Publication-quality figures | Phase 4 completion |
| **6. Manuscript** | 3 Weeks | Complete scientific paper | Phase 5 completion |
| **7. Review & Submission** | 2 Weeks | Journal submission | Phase 6 completion |

**Total Estimated Time:** ~12 Weeks (3 months)

---

## 🎯 **Success Metrics**

### **Technical Achievements**

- ✅ Successful ingestion of 27.6GB DESI DR1 data
- ✅ Robust environmental classification algorithm
- ✅ Statistical significance in environmental effects
- ✅ Publication-quality analysis workflow

### **Scientific Impact**

- 🏆 **Precision Measurement:** Most definitive quantification of void environment effects
- 📋 **Community Resource:** Value-Added Catalog with environmental classifications
- 🧮 **Theory Validation:** Critical constraints for cosmological simulations
- ⚡ **Early Results:** First major publication demonstrating research capabilities

### **Infrastructure Validation**

- 🖥️ **Platform Demonstration:** Successful PostgreSQL-based analysis workflow
- 📊 **Scalability Proof:** Framework extensible to additional environmental studies
- 🔧 **Operational Excellence:** Systematic backup, monitoring, and maintenance procedures

---

## 🔗 **Dependencies & Integration**

### **Infrastructure Dependencies**

- **Database Server:** proj-pg01 with PostgreSQL 16 optimization
- **Analysis Platform:** proj-dp01 for Python scientific computing
- **Backup Infrastructure:** pbs01 for systematic data protection
- **Network Connectivity:** High-bandwidth access for data download

### **External Dependencies**

- **DESI DR1 Data Access:** Stable access to public data releases
- **Q3C Extension:** Spatial indexing for astronomical coordinates
- **Python Scientific Stack:** Maintained versions of core libraries

### **Project Integration**

- **Documentation Framework:** Comprehensive methodology documentation
- **Quality Assurance:** Statistical rigor and reproducibility validation
- **Community Engagement:** Open data release and collaboration support

---

This roadmap provides systematic guidance for transforming DESI DR1 data into precision measurements of environmental effects on galaxy evolution, delivering both scientific results and community data products while validating research infrastructure and analytical capabilities.
