# Comprehensive Test Cases & Validation Matrix

The platform is covered by an automated test suite comprising **62 pytest test cases** across 3 modules:

---

### Test Module 1: System Architecture & Configuration (`tests/test_phase1_setup.py`)

| Test ID | Test Method Name | Description | Expected Outcome | Status |
|---|---|---|---|---|
| **TC-01** | `test_required_directories_exist` | Validates presence of all 18 core project directories (`backend/`, `bigdata/`, `data/`, etc.). | All directories exist on disk | ✅ PASS |
| **TC-02** | `test_required_files_exist` | Verifies essential code, config, and script files are present. | All 15 required files exist | ✅ PASS |
| **TC-03** | `test_env_example_has_required_keys` | Verifies `.env.example` has all deployment keys (`FLASK_SECRET_KEY`, `STORAGE_MODE`, etc.). | All keys defined | ✅ PASS |
| **TC-04** | `test_env_example_does_not_contain_real_secrets` | Audits `.env.example` for inadvertent hardcoded API secrets. | No real credentials exposed | ✅ PASS |
| **TC-05** | `test_config_loads_without_error` | Tests `backend.config.Config` initialization from environment. | Default settings loaded safely | ✅ PASS |
| **TC-06** | `test_config_summary_is_safe` | Verifies secret keys are scrubbed from public config summaries. | No secrets in summary | ✅ PASS |
| **TC-07** | `test_allowed_file_csv` | Checks validator allows valid `.csv` filenames. | Returns True | ✅ PASS |
| **TC-08** | `test_allowed_file_reject_exe` | Checks validator rejects dangerous file extensions (`.exe`). | Returns False | ✅ PASS |
| **TC-09** | `test_validate_csv_columns_ok` | Validates column checker passes when required headers exist. | Returns (True, "") | ✅ PASS |
| **TC-10** | `test_validate_csv_columns_missing` | Validates column checker rejects CSV missing mandatory headers. | Returns False with missing list | ✅ PASS |
| **TC-11** | `test_sanitise_filename` | Tests directory traversal prevention (`../../etc/passwd`). | Strips traversal components | ✅ PASS |
| **TC-12** | `test_liveness_returns_200` | Tests `GET /api/v1/health` endpoint. | Status 200, success=True | ✅ PASS |
| **TC-13** | `test_detail_has_components` | Tests `GET /api/v1/health/detail` returns DB, Spark, and Storage info. | Status 200 with component dict | ✅ PASS |
| **TC-14** | `test_404_returns_json` | Verifies 404 handler returns structured JSON error envelope. | Status 404, success=False | ✅ PASS |

---

### Test Module 2: Ingestion & Storage Abstraction (`tests/test_phase2_ingestion.py`)

| Test ID | Test Method Name | Description | Expected Outcome | Status |
|---|---|---|---|---|
| **TC-15** | `test_sample_files_exist_or_can_be_generated` | Verifies all 4 sample CSVs are generated in `data/sample/`. | 4 files present | ✅ PASS |
| **TC-16** | `test_sample_shipments_has_required_columns` | Verifies generated shipments CSV conforms to required schema. | All required columns present | ✅ PASS |
| **TC-17** | `test_sample_shipments_is_labelled_synthetic` | Audits sample data disclosure for ethical academic provenance. | Labelled as SYNTHETIC | ✅ PASS |
| **TC-18** | `test_sample_shipments_delay_rate_is_reasonable` | Verifies empirical delay probability is between 20% and 70%. | Rate within realistic window | ✅ PASS |
| **TC-19** | `test_no_duplicate_shipment_ids` | Verifies uniqueness of primary keys across sample records. | All IDs unique | ✅ PASS |
| **TC-20** | `test_gps_coordinates_in_valid_range` | Verifies latitude [-90, 90] and longitude [-180, 180] validity. | All waypoints geographically valid | ✅ PASS |
| **TC-21** | `test_storage_service_initialises` | Tests storage service initialises in local mode by default. | Mode is 'local' | ✅ PASS |
| **TC-22** | `test_save_and_retrieve_file` | Verifies saving and reading files through storage abstraction. | File contents preserved | ✅ PASS |
| **TC-23** | `test_ingest_valid_shipments_csv` | Tests end-to-end ingestion pipeline on a test CSV. | Records read >= inserted | ✅ PASS |
| **TC-24** | `test_ingest_empty_csv_reports_error` | Tests parser rejects 0-byte CSV files gracefully. | Returns success=False | ✅ PASS |
| **TC-25** | `test_upload_valid_shipments` | Tests `POST /api/v1/upload/shipments` multipart endpoint. | Status 201 Created | ✅ PASS |
| **TC-26** | `test_upload_wrong_extension_returns_400` | Tests uploading `.xlsx` file is rejected with 400. | Status 400 Validation Error | ✅ PASS |

---

### Test Module 3: Big Data Processing, ML & APIs (`tests/test_phase3_bigdata_ml.py`)

| Test ID | Test Method Name | Description | Expected Outcome | Status |
|---|---|---|---|---|
| **TC-27** | `test_mapreduce_pipeline_execution` | Tests `run_mapreduce_job` executes mapper, sort, and reducer. | Aggregates 390+ records | ✅ PASS |
| **TC-28** | `test_mapreduce_categories_emitted` | Verifies MapReduce emits keys for route, carrier, vehicle, overall. | All categories present | ✅ PASS |
| **TC-29** | `test_shipment_etl_processor` | Tests Spark ETL deduplication and type casting. | Clean dataset saved | ✅ PASS |
| **TC-30** | `test_route_analyzer` | Tests Spark route risk categorization (Low/Medium/High). | Route table generated | ✅ PASS |
| **TC-31** | `test_delay_aggregator` | Tests multi-dimensional aggregation across carriers & vehicles. | KPI dictionary generated | ✅ PASS |
| **TC-32** | `test_feature_engineering_no_target_leakage` | **CRITICAL AUDIT**: Verifies exclusion of actual delivery times. | No leakage columns in X | ✅ PASS |
| **TC-33** | `test_model_training_and_evaluation` | Trains baseline LR and Random Forest; verifies 2x2 confusion matrix. | Models trained, report saved | ✅ PASS |
| **TC-34** | `test_single_shipment_prediction` | Tests inference engine returns risk tier, confidence, and factors. | Prediction schema valid | ✅ PASS |
| **TC-35** | `test_predict_endpoint` | Tests `POST /api/v1/predict` endpoint with JSON payload. | Status 200, risk returned | ✅ PASS |
| **TC-36** | `test_shipments_list_endpoint` | Tests `GET /api/v1/shipments` pagination and filtering. | Returns paginated list | ✅ PASS |
| **TC-37** | `test_analytics_endpoints` | Tests all analytical API routes feed structured chart payloads. | All routes return status 200 | ✅ PASS |
| **TC-38** | `test_frontend_pages_render` | Tests all 7 frontend HTML templates render without 5xx errors. | Status 200 for all views | ✅ PASS |

