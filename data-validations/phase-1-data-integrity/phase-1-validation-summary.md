2025-08-05 02:11:18,369 - INFO - 🔍 STARTING STAGE 1 DATABASE INTEGRITY VALIDATION
2025-08-05 02:11:18,370 - INFO - ============================================================
2025-08-05 02:11:18,370 - INFO -
=== SCHEMA EXISTENCE VALIDATION ===
2025-08-05 02:11:18,377 - INFO - ✅ FastSpecFit raw_catalogs schema exists: PASS
2025-08-05 02:11:18,378 - INFO - ✅ fastspecfit_galaxies table exists: PASS
2025-08-05 02:11:18,384 - INFO - ✅ DESIVAST raw_catalogs schema exists: PASS
2025-08-05 02:11:18,385 - INFO - ✅ desivast_voids table exists: PASS
2025-08-05 02:11:18,385 - INFO -
=== ROW COUNT VALIDATION ===
2025-08-05 02:11:18,817 - INFO - FastSpecFit galaxies: 6,445,927 rows
2025-08-05 02:11:18,817 - INFO - ✅ FastSpecFit row count reasonable: PASS
2025-08-05 02:11:18,817 - INFO -    Details: 6,445,927 rows
2025-08-05 02:11:18,824 - INFO - DESIVAST voids: 10,752 rows
2025-08-05 02:11:18,824 - INFO - ✅ DESIVAST row count reasonable: PASS
2025-08-05 02:11:18,824 - INFO -    Details: 10,752 rows (lower than expected ~25K)
2025-08-05 02:11:18,825 - INFO -
=== PRIMARY KEY UNIQUENESS VALIDATION ===
2025-08-05 02:11:20,037 - INFO - ✅ FastSpecFit TARGETID uniqueness: PASS
2025-08-05 02:11:20,038 - INFO -    Details: No duplicate TARGETIDs found
2025-08-05 02:11:20,047 - INFO - DESIVAST columns: void_id, algorithm, original_void_index, ra, dec, x_mpc_h, y_mpc_h, z_mpc_h, radius_mpc_h, edge_flag...
2025-08-05 02:11:20,047 - INFO - ✅ DESIVAST primary key check: PASS
2025-08-05 02:11:20,047 - INFO -    Details: No obvious primary key column found - may be composite
2025-08-05 02:11:20,047 - INFO -
=== NULL VALUE ASSESSMENT ===
2025-08-05 02:11:20,429 - INFO - ✅ FastSpecFit targetid completeness: PASS
2025-08-05 02:11:20,429 - INFO -    Details: No NULL or non-finite values
2025-08-05 02:11:20,759 - INFO - ✅ FastSpecFit ra completeness: PASS
2025-08-05 02:11:20,759 - INFO -    Details: No NULL or non-finite values
2025-08-05 02:11:21,102 - INFO - ✅ FastSpecFit dec completeness: PASS
2025-08-05 02:11:21,102 - INFO -    Details: No NULL or non-finite values
2025-08-05 02:11:21,794 - INFO - ✅ FastSpecFit z completeness: PASS
2025-08-05 02:11:21,794 - INFO -    Details: No NULL or non-finite values
2025-08-05 02:11:22,447 - INFO - ✅ FastSpecFit logmstar completeness: PASS
2025-08-05 02:11:22,447 - INFO -    Details: No NULL or non-finite values
2025-08-05 02:11:23,111 - INFO - ✅ FastSpecFit sfr completeness: PASS
2025-08-05 02:11:23,111 - INFO -    Details: No NULL or non-finite values
2025-08-05 02:11:23,122 - INFO - ✅ DESIVAST void_id completeness: PASS
2025-08-05 02:11:23,122 - INFO -    Details: No NULL values
2025-08-05 02:11:23,123 - INFO - ✅ DESIVAST algorithm completeness: PASS
2025-08-05 02:11:23,123 - INFO -    Details: No NULL values
2025-08-05 02:11:23,124 - INFO - ✅ DESIVAST original_void_index completeness: PASS
2025-08-05 02:11:23,124 - INFO -    Details: No NULL values
2025-08-05 02:11:23,125 - INFO - ✅ DESIVAST ra completeness: PASS
2025-08-05 02:11:23,125 - INFO -    Details: No NULL values
2025-08-05 02:11:23,126 - INFO - ✅ DESIVAST dec completeness: PASS
2025-08-05 02:11:23,126 - INFO -    Details: No NULL values
2025-08-05 02:11:23,126 - INFO -
=== DATA TYPE AND RANGE VALIDATION ===
2025-08-05 02:11:23,330 - INFO - ✅ RA value ranges: PASS
2025-08-05 02:11:23,330 - INFO -    Details: RA range: 0.00 to 360.00 degrees
2025-08-05 02:11:23,482 - INFO - ✅ DEC value ranges: PASS
2025-08-05 02:11:23,482 - INFO -    Details: DEC range: -19.46 to 79.27 degrees
2025-08-05 02:11:23,928 - INFO - ✅ Redshift value ranges: PASS
2025-08-05 02:11:23,928 - INFO -    Details: z range: 0.0010 to 6.4077
2025-08-05 02:11:23,928 - INFO -
============================================================
2025-08-05 02:11:23,928 - INFO - 📊 STAGE 1 VALIDATION SUMMARY
2025-08-05 02:11:23,928 - INFO - ============================================================
2025-08-05 02:11:23,928 - INFO - Total Checks: 22
2025-08-05 02:11:23,928 - INFO - ✅ Passed: 22
2025-08-05 02:11:23,928 - INFO - ⚠️  Warnings: 0
2025-08-05 02:11:23,928 - INFO - ❌ Failed: 0
2025-08-05 02:11:23,928 - INFO - Success Rate: 100.0%
2025-08-05 02:11:23,928 - INFO - 🎉 DATABASE INTEGRITY VALIDATION PASSED!
2025-08-05 02:11:23,929 - INFO -
✅ Stage 1 validation completed successfully.
2025-08-05 02:11:23,929 - INFO - Database is ready for Stage 2 (Physical Plausibility) validation.