# Dataset Card: DESI Cosmic Void Galaxy Catalog v1.0

## Overview

**DESI Cosmic Void Galaxy Catalog** is a science-ready dataset of **6.4 million galaxies** from DESI Data Release 1, uniquely enriched with cosmic void environmental context. This dataset enables precision studies of environmental quenching—how the large-scale cosmic environment affects galaxy star formation and evolution.

**Key Innovation**: First large-scale extragalactic catalog combining deep environmental classification (void vs. wall galaxies) with comprehensive physical properties at DESI survey scale.

---

## Quick Facts

| Attribute | Value |
|-----------|-------|
| **Total Galaxies** | 6,445,927 |
| **Cosmic Voids** | ~10,752 (4 algorithms: VIDE, ZOBOV, REVOLVER, VoidFinder) |
| **Redshift Range** | z = 0.001 - 1.02 (median ~0.31) |
| **Sky Coverage** | Full DESI DR1 footprint (NGC + SGC) |
| **Data Volume** | ~30GB (PostgreSQL) → ~3-5GB (Parquet release) |
| **Primary Science** | Environmental quenching in cosmic voids |
| **License** | CC BY 4.0 |
| **DOI** | [To be assigned] |

---

## Scientific Motivation

### The Nature vs. Nurture Problem

Are galaxy properties determined by **intrinsic mass** (nature) or **environmental interactions** (nurture)? This dataset provides the statistical power to answer this question by comparing galaxies in extreme environments:

- **Cosmic Voids**: Ultimate "field" environment—low density, minimal interactions
- **Cosmic Walls**: Dense filamentary structures—high merger rates, environmental processing

### Research Applications

- ✅ Precision measurement of environmental quenching effects
- ✅ Galaxy stellar mass function variations by environment  
- ✅ Star formation suppression mechanisms at large scales
- ✅ Machine learning benchmarks for galaxy evolution
- ✅ Graph Neural Network (GNN) applications to large-scale structure

---

## Data Provenance & Processing

### Source Catalogs

**1. DESIVAST Void Catalog (Official DESI DR1 VAC)**

- **Purpose**: Cosmic void identification using 4 algorithms
- **Algorithms**: VIDE, ZOBOV, REVOLVER, VoidFinder
- **Key Metrics**: Void positions (RA/Dec/z), effective radii, edge flags
- **Coverage**: NGC (North Galactic Cap) + SGC (South Galactic Cap)

**2. FastSpecFit Galaxy Properties (DESI DR1 VAC)**

- **Purpose**: Stellar population synthesis results
- **Key Properties**: Stellar mass, star formation rate (SFR), age, metallicity
- **Method**: Spectral fitting of DESI spectra
- **Quality**: Validated against SDSS/literature benchmarks

### Processing Pipeline

```markdown
DESI DR1 FITS Files (27.6GB)
    ↓
[2025-07-02] FITS Inspection & Download
    ↓
[2025-07-14] PostgreSQL Ingestion (COPY-based, 150k rows/sec)
    ├─ desivast_voids (raw_catalogs schema)
    └─ fastspecfit_galaxies (raw_catalogs schema)
    ↓
[2025-08-04] Stage 1 Validation (integrity checks)
    ├─ Row counts: 6.4M galaxies ✓
    ├─ PK uniqueness ✓
    └─ Null/type sanity ✓
    ↓
[2025-08-05] Stage 2 Validation (physical plausibility)
    ├─ Redshift range: z ∈ [0.001, 1.02] ✓
    ├─ Mass-z correlation (Malmquist bias) ✓
    └─ Retention: 98.4% post-cuts ✓
    ↓
[2025-10-04] Final Dataset Packaging
    └─ Multi-format release (Parquet, FITS, PostgreSQL dump)
```

**Processing Infrastructure**:

- **Database**: PostgreSQL 16 on proj-pg01 (8 vCPU, 48GB RAM, Samsung PM983 NVMe)
- **Storage Performance**: 3,000 MB/s read, 1,400 MB/s write, 480K IOPS random read
- **Spatial Indexing**: GIST(ra, dec) for <1s proximity queries on 6.4M rows

---

## Dataset Structure

### File Organization

```markdown
desi-void-galaxies-v1.0/
├── data/
│   ├── galaxies_core.parquet          # Main galaxy catalog (6.4M rows)
│   ├── voids_unified.parquet           # All voids (4 algorithms, 10.7K voids)
│   ├── galaxy_void_assignments.parquet # Environmental classifications
│   └── sample_10k.parquet              # Quick-start subset
├── docs/
│   ├── README.md                       # This file
│   ├── DATA_DICTIONARY.md              # Detailed schema
│   ├── VALIDATION_REPORT.md            # Quality assurance results
│   └── CITATION.cff                    # Citation metadata
├── notebooks/
│   ├── 01_quickstart.ipynb             # Load & visualize in 5 min
│   ├── 02_void_analysis.ipynb          # Environmental quenching example
│   └── 03_advanced_features.ipynb      # Derived metrics tutorial
└── metadata/
    ├── manifest.csv                    # File inventory + checksums
    ├── schema_galaxies.json            # Auto-generated schema
    └── processing_log.txt              # Full pipeline history
```

### Primary Data Files

**1. `galaxies_core.parquet`** (Main Catalog)

- **Rows**: 6,445,927
- **Columns**: 15 core + derived features
- **Index**: `targetid` (DESI unique identifier)
- **Partitioning**: By healpix_id for parallel processing
- **Typical Use**: Load entire catalog for analysis

**2. `voids_unified.parquet`** (Void Catalog)

- **Rows**: ~10,752 voids across 4 algorithms
- **Key Fields**: algorithm, ra, dec, redshift, radius_mpc_h, r_eff, galactic_cap
- **Typical Use**: Void population studies, cross-matching

**3. `galaxy_void_assignments.parquet`** (Environmental Labels)

- **Rows**: 6,445,927 (1:1 with galaxies_core)
- **Key Fields**: targetid, environment ('void'/'wall'), nearest_void_id, void_centric_radius_norm
- **Typical Use**: Environmental quenching analysis, sample selection

---

## Schema Overview

### Galaxy Properties (`galaxies_core.parquet`)

| Column | Type | Unit | Description | Notes |
|--------|------|------|-------------|-------|
| **targetid** | int64 | - | DESI unique identifier | Primary key |
| **ra** | float64 | degrees | Right Ascension (J2000) | Range: [0.01°, 359.99°] |
| **dec** | float64 | degrees | Declination (J2000) | Range: [-89.5°, 89.5°] |
| **z** | float64 | - | Spectroscopic redshift | Range: [0.001, 1.02] |
| **z_err** | float64 | - | Redshift uncertainty | Median ~0.0001 |
| **logmstar** | float32 | log₁₀(M☉) | Log stellar mass | FastSpecFit derived |
| **logmstar_err** | float32 | dex | Stellar mass uncertainty | Typical ~0.1 dex |
| **sfr** | float32 | M☉/yr | Star formation rate | FastSpecFit derived |
| **sfr_err** | float32 | M☉/yr | SFR uncertainty | - |
| **age_gyr** | float32 | Gyr | Luminosity-weighted age | - |
| **metallicity** | float32 | - | Mass-weighted metallicity | - |
| **d4000** | float32 | - | 4000Å break strength | Quenching indicator |
| **healpix_id** | int32 | - | HEALPix pixel (source file) | For data provenance |
| **source_file** | string | - | Original FITS filename | Traceability |
| **ingestion_timestamp** | datetime | - | Processing timestamp | Data lineage |

**Derived Columns** (if included in v1.0—defer to v1.1 if time-constrained):

- `local_density`: k-NN density estimate (galaxies/Mpc³)
- `void_centric_r_norm`: Normalized distance from void center (for void galaxies)
- `quenching_state`: Categorical flag (0=SF, 1=Green Valley, 2=Quiescent)

### Void Properties (`voids_unified.parquet`)

| Column | Type | Unit | Description | Algorithm Availability |
|--------|------|------|-------------|----------------------|
| **void_id** | int32 | - | Unique void identifier | All |
| **algorithm** | string | - | Void-finding method | VIDE/ZOBOV/REVOLVER/VoidFinder |
| **original_void_index** | int64 | - | Index in source FITS | All |
| **ra** | float64 | degrees | Void center RA | All |
| **dec** | float64 | degrees | Void center Dec | All |
| **redshift** | float64 | - | Void center redshift | All |
| **x_mpc_h**, **y_mpc_h**, **z_mpc_h** | float64 | Mpc/h | Comoving coordinates | All |
| **radius_mpc_h** | float64 | Mpc/h | Void radius | All |
| **r_eff** | float64 | Mpc/h | Effective radius | VoidFinder only |
| **r_eff_uncert** | float64 | Mpc/h | Effective radius uncertainty | VoidFinder only |
| **edge_flag** | int32 | - | Edge proximity flag (1=edge) | All |
| **galactic_cap** | string | - | NGC or SGC | All |
| **source_file** | string | - | Original FITS filename | All |

**Algorithm-Specific Notes**:

- **VoidFinder**: Uses "maximal spheres" method, provides `r_eff` uncertainties
- **ZOBOV**: Watershed-based, includes `depth`, `tot_area`, `edge_area` fields (see full schema)
- **VIDE**: Parameter-space void identification
- **REVOLVER**: Machine learning-informed void detection

### Environmental Assignments (`galaxy_void_assignments.parquet`)

| Column | Type | Description |
|--------|------|-------------|
| **targetid** | int64 | Links to galaxies_core |
| **environment** | string | 'void' or 'wall' |
| **nearest_void_id** | int32 | Closest void (null for wall galaxies) |
| **nearest_void_algorithm** | string | Algorithm of nearest void |
| **distance_to_void_center_mpc** | float64 | 3D comoving distance |
| **void_centric_radius_norm** | float64 | distance / void_radius (null if wall) |
| **in_void_interior** | bool | True if r_norm < 1.0 |

---

## Data Quality & Validation

### Validation Results Summary

**Stage 1: Integrity Checks** (2025-08-04)

- ✅ Row count: 6,445,927 galaxies (matches FastSpecFit DR1)
- ✅ Primary key uniqueness: 100% (targetid)
- ✅ Null rates: <0.02% on critical columns (logmstar, sfr)
- ✅ Type consistency: All numeric fields validated

**Stage 2: Physical Plausibility** (2025-08-05)

- ✅ Redshift range: z ∈ [0.001, 1.02] (DESI BGS expected)
- ✅ Mass-redshift correlation: Strong Malmquist-like selection bias observed (expected)
- ✅ Retention post-cuts: 98.4% (~6,342,556 galaxies)
- ✅ Spatial coverage: Full-sky DESI footprint confirmed

**Stage 3: Systematic Uncertainties** (2025-08-05 PM)

- ✅ Cross-algorithm void comparison (KS/MW tests)
- ✅ Mean Δ quenched fraction ≈ 0.0266 across algorithms
- ✅ Cohen's d ≈ 0.0625 (small systematic effect)

### Known Limitations

1. **Redshift Range**: Optimized for DESI Bright Galaxy Survey (BGS), z < 0.6 best coverage
2. **Mass Completeness**: Malmquist bias—higher-z sample is mass-selected
3. **Void Edge Effects**: `edge_flag=1` voids may have truncated shapes (survey boundaries)
4. **Algorithm Differences**: Void definitions vary by method (see systematic analysis)
5. **Missing Spectra**: ~2% of DESI targets lack reliable FastSpecFit parameters

### Quality Flags (Use These!)

**For galaxies**:

- Filter by `z_err < 0.001` for high-confidence redshifts
- Use `logmstar_err < 0.2` for mass-selected samples
- Check `source_file` if investigating healpix-specific systematics

**For voids**:

- Exclude `edge_flag=1` for complete void shapes
- Compare across `algorithm` to assess systematic uncertainties
- Use `r_eff_uncert` (VoidFinder only) for uncertainty propagation

---

## Usage Examples

### Quick Start (Python)

```python
import pandas as pd

# Load main catalog
galaxies = pd.read_parquet('data/galaxies_core.parquet')
env = pd.read_parquet('data/galaxy_void_assignments.parquet')

# Merge environmental context
df = galaxies.merge(env, on='targetid')

# Select void galaxies
void_gals = df[df['environment'] == 'void']

# Basic analysis: quenched fraction in voids vs. walls
quenched = df['sfr'] < 0.3 * 10**(df['logmstar'] - 10)  # sSFR cut
print(f"Void quenched fraction: {quenched[df['environment']=='void'].mean():.3f}")
print(f"Wall quenched fraction: {quenched[df['environment']=='wall'].mean():.3f}")
```

### Advanced: Void-Centric Analysis

```python
import numpy as np
from astropy.cosmology import FlatLambdaCDM

cosmo = FlatLambdaCDM(H0=70, Om0=0.3)  # DESI DR1 cosmology

# Bin by normalized void-centric radius
void_interior = df[df['in_void_interior'] == True]
bins = np.linspace(0, 1, 5)
void_interior['r_bin'] = pd.cut(void_interior['void_centric_radius_norm'], bins)

# Quenched fraction vs. radius
quench_vs_radius = void_interior.groupby('r_bin').apply(
    lambda x: (x['sfr'] < 0.3 * 10**(x['logmstar'] - 10)).mean()
)
print(quench_vs_radius)
```

See `notebooks/02_void_analysis.ipynb` for full reproducible example.

---

## Citation & Attribution

### How to Cite

If you use this dataset, please cite:

```bibtex
@dataset{desi_void_galaxies_2025,
  author = {[Your Name/Team]},
  title = {DESI Cosmic Void Galaxy Catalog v1.0},
  year = {2025},
  publisher = {Zenodo},
  doi = {[To be assigned]},
  url = {[Dataset URL]}
}
```

### Acknowledge Source Data

This dataset builds upon:

- **DESIVAST**: DESI DR1 void catalog (cite: arXiv:2410.XXXXX)
- **FastSpecFit**: DESI DR1 galaxy properties VAC (cite DESI DR1 paper)
- **DESI Collaboration**: Data Release 1 (cite: [DESI DR1 overview paper])

### License

Creative Commons Attribution 4.0 International (CC BY 4.0)

You are free to:

- ✅ Share, copy, redistribute
- ✅ Adapt, transform, build upon
- ✅ Use for commercial purposes

Under these terms:

- **Attribution**: Must credit original authors and cite dataset DOI
- **Indicate Changes**: If you modify the data, state changes clearly

---

## Technical Details

### Cosmology

All distance calculations use **Planck 2018 cosmology**:

- H₀ = 70 km/s/Mpc (DESI DR1 standard)
- Ωₘ = 0.3
- ΩΛ = 0.7
- Flat universe (Ωₖ = 0)

### Coordinate Systems

- **Equatorial**: RA/Dec in J2000 epoch
- **Comoving**: (x, y, z) in Mpc/h for void centers
- **Redshift**: Spectroscopic (DESI pipeline processed)

### File Formats

- **Parquet**: Columnar storage, ~10x smaller than CSV, fast partial reads
- **FITS** (optional): Available on request for VO compliance
- **PostgreSQL dump** (optional): Full database export for local deployment

### Reproducibility

All processing scripts available at:

- **GitHub**: [desi-cosmic-void-galaxies repo]
- **Worklogs**: Timestamped development history (see `docs/worklogs/`)
- **Validation**: Complete test suite in `validation/` directory

**Software Environment**:

- Python 3.11.5, PostgreSQL 16.1
- Key libraries: Astropy 5.3, pandas 2.0, psycopg2-binary 2.9.9
- Full dependency list: `environment.yml`

---

## Future Enhancements (Roadmap)

**v1.1 (Planned Q1 2026)**:

- ✨ Pre-computed tabular embeddings (autoencoder, 16-32 dim)
- ✨ Derived features: local density, structural parameters (concentration, B/T)
- ✨ Categorical quenching state flags

**v2.0 (Research Phase)**:

- 🔬 GNN-ready data structures (node/edge Parquet files)
- 🔬 Self-supervised spectral embeddings (if raw spectra accessed)
- 🔬 Causal inference features (propensity scores for matching)

**Community Contributions Welcome**:

- See `CONTRIBUTING.md` for guidelines
- Open issues for feature requests or bug reports

---

## Support & Contact

**Primary Contact**: [Your Email]  
**Project Repository**: [GitHub URL]  
**Issue Tracker**: [GitHub Issues URL]  
**Discussion Forum**: [GitHub Discussions or equivalent]

**Preferred Contact Method**: Open a GitHub issue for:

- ❓ Usage questions → tag `question`
- 🐛 Data quality concerns → tag `bug`
- 💡 Feature requests → tag `enhancement`

---

## Acknowledgments

**Infrastructure**: Proxmox Astronomy Lab

- proj-pg01: PostgreSQL 16 primary database (8 vCPU, 48GB RAM, Samsung PM983 NVMe)
- proj-dp01: Python processing workstation (4 vCPU, 16GB RAM)

**Data Sources**:

- DESI Collaboration for DR1 public data release
- DESIVAST team for void catalog
- FastSpecFit team for galaxy properties

**Methodology Inspiration**:

- SDSS Value-Added Catalog program
- Gaia DR3 ML enrichment strategies
- Cross-domain ML-ready dataset best practices (HLS, AlphaFold)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | 2025-10-04 | Initial public release (6.4M galaxies, 10.7K voids) |
