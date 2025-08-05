2025-08-05 01:44:23,585 - INFO - Running validation on FULL dataset for maximum accuracy
2025-08-05 01:44:23,585 - INFO - 🔬 STARTING STAGE 2 PHYSICAL PLAUSIBILITY VALIDATION
2025-08-05 01:44:23,585 - INFO - ======================================================================
2025-08-05 01:44:23,585 - INFO - Loading datasets...
2025-08-05 01:44:23,585 - INFO - Loading galaxy data from FastSpecFit catalog...
2025-08-05 01:44:23,592 - INFO - Executing query... (this may take a few minutes for full dataset)
2025-08-05 01:44:50,948 - INFO - Calculating derived quantities...
2025-08-05 01:44:51,093 - INFO - Loaded 6,342,556 galaxies with relaxed quality cuts applied
2025-08-05 01:44:51,093 - INFO - Quality cuts removed ~1.6% of raw data
2025-08-05 01:44:51,093 - INFO - Loading void data from DESIVAST catalog...
2025-08-05 01:44:51,132 - INFO - Loaded 10,752 voids across algorithms: ['REVOLVER' 'VIDE' 'ZOBOV' 'VoidFinder']
2025-08-05 01:44:51,132 - INFO -
=== GENERATING DISTRIBUTION DIAGNOSTICS ===
2025-08-05 01:44:51,975 - INFO - ✅ Stellar mass distribution: PASS
2025-08-05 01:44:51,975 - INFO -    Survey-appropriate range: 6.0 to 13.0
2025-08-05 01:44:53,217 - INFO - ✅ SFR distribution: PASS
2025-08-05 01:44:53,217 - INFO -    No negative SFR values
2025-08-05 01:44:54,664 - INFO - ✅ D4000 distribution: PASS
2025-08-05 01:44:54,664 - INFO -    Excellent range after quality cuts: 0.50 to 5.00
2025-08-05 01:44:54,664 - INFO - ✅ Distribution diagnostics: COMPLETE
2025-08-05 01:44:54,664 - INFO -    Generated 4 distribution plots
2025-08-05 01:44:54,664 - INFO -
=== GENERATING SCALING RELATION DIAGNOSTICS ===
2025-08-05 01:44:56,171 - WARNING - ⚠️  Mass-Redshift Correlation: Strong correlation r=0.614 - consistent with survey selection (Malmquist bias)
2025-08-05 01:44:57,492 - INFO - ✅ Main Sequence Slope: PASS
2025-08-05 01:44:57,492 - INFO -    Slope 1.01 within expected range
2025-08-05 01:44:59,574 - INFO - ✅ Scaling relations: COMPLETE
2025-08-05 01:44:59,574 - INFO -    Generated 3 scaling relation plots
2025-08-05 01:44:59,574 - INFO -
=== ANALYZING VOID-FINDER SYSTEMATICS ===
2025-08-05 01:44:59,574 - INFO - Found algorithms: ['REVOLVER' 'VIDE' 'ZOBOV' 'VoidFinder']
2025-08-05 01:45:00,413 - INFO - Void size statistics by algorithm:
2025-08-05 01:45:00,415 - INFO -
            count       mean        std     median
algorithm
REVOLVER     1992  17.240796   5.677797  15.876529
VIDE         1478  17.246640   6.634247  15.382068
VoidFinder   3765  12.601485   2.277420  11.927976
ZOBOV        3517  13.723826  11.999877  11.500294
2025-08-05 01:45:02,784 - INFO - ✅ Void count variation: PASS
2025-08-05 01:45:02,784 - INFO -    Reasonable count variation (ratio: 2.5)
2025-08-05 01:45:02,784 - INFO - ✅ Void size consistency: PASS
2025-08-05 01:45:02,784 - INFO -    Good size consistency (ratio: 1.4)
2025-08-05 01:45:02,784 - INFO - ✅ Void systematics: COMPLETE
2025-08-05 01:45:02,784 - INFO -    Analyzed 4 algorithms
2025-08-05 01:45:02,784 - INFO -
=== GENERATING VALIDATION SUMMARY ===
2025-08-05 01:45:04,028 - INFO - Summary report saved to validation_data/stage2_summary.txt
2025-08-05 01:45:04,028 - INFO -
======================================================================

2025-08-05 01:45:04,028 - INFO - 📊 STAGE 2 VALIDATION SUMMARY
2025-08-05 01:45:04,028 - INFO - ======================================================================
2025-08-05 01:45:04,028 - INFO - 🚨 Red Flags: 0
2025-08-05 01:45:04,028 - INFO - ⚠️  Warnings: 1
2025-08-05 01:45:04,028 - INFO - 📈 Plots Generated: 10
2025-08-05 01:45:04,029 - INFO - 🎉 PHYSICAL PLAUSIBILITY VALIDATION PASSED!
2025-08-05 01:45:04,029 - INFO - Data appears scientifically sound for cosmic void analysis.
2025-08-05 01:45:04,029 - INFO -
✅ Stage 2 validation completed successfully.
2025-08-05 01:45:04,029 - INFO - Data is ready for scientific void analysis.
2025-08-05 01:45:04,029 - INFO -
Generated plots available in validation_plots/
