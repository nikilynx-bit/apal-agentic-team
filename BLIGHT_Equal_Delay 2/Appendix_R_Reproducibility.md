# Appendix R - BLIGHT matched-seed deployment-delay sensitivity

**Status:** Actually executed Python simulation; development-test fixtures only; not Aceh-calibrated.

## R1. Simulation manifest

The original BLIGHT v0.1 source is supplied unchanged. The sensitivity driver overrides only `POLICIES["B"]["install_delay"]` from 3 weeks to 1 week. Policy A retains one week. All other economic, hazard, budget and household parameters remain identical.

- Model source SHA-256: `8b2a7de18601f7665d5cc5f2d8db7c0fdfb632f9c8b5f13aa6ec99d65b96957b`
- Driver SHA-256: `c8bf2d23c67c10f56b76bef977e52b6d64daa2c62e6cc757548031705e63b256`
- Python version: 3.13.5; standard library only for the simulation.
- Scenarios: S1, S2, S3, S4; seeds: 1-8; 52 weekly steps; 600 actors (360 households); shock week 27.
- 64 actual reruns: 32 original A control replays and 32 equal-delay B sensitivity runs; 32 historical A and B pairs also read from original 96-run CSV.
- Randomisation: matching scenario/seed generates common synthetic household traits, weather stream and acceptance random draws for each A/B comparison.
- Synthetic welfare outcome: mean across households of each household's mean weekly welfare index. No empirical welfare measurement.
- Baseline A replay reproduced the recorded six-decimal welfare for all 32 runs exactly.
- One complete 52-step trace per A-original and B-equal-delay is in `results/complete_HH_0001_decision_trace.csv` and a JSONL copy.
- Warning: model generated identical `run_id` labels for baseline B and sensitivity B; provenance is distinguished by the experiment ID and separate folders.

### Parameters

| Parameter | A baseline | B baseline | B equal delay |
|---|---:|---:|---:|
| shelter_cost | 2400 | 5000 | 5000 |
| public_share | 0.8 | 0.65 | 0.65 |
| flood_protection | 0.22 | 0.69 | 0.69 |
| heat_protection | 0.2 | 0.68 | 0.68 |
| maintenance_rate | 0.014 | 0.008 | 0.008 |
| retrofit_cost | 3100 | 1200 | 1200 |
| retrofit_gain | 0.3 | 0.14 | 0.14 |
| install_delay | 1 | 3 | 1 |

## R2. Observed synthetic welfare results

| Scenario | N matched | Baseline B-A | Equal-delay B-A | Improvement | B wins equal delay |
|---|---:|---:|---:|---:|---:|
| S1 | 8 | -2.329 | -0.717 | +1.612 | 0 |
| S2 | 8 | -2.227 | -0.615 | +1.612 | 0 |
| S3 | 8 | -2.006 | -0.397 | +1.609 | 0 |
| S4 | 8 | -1.572 | +0.007 | +1.579 | 4 |
| ALL | 32 | -2.033 | -0.430 | +1.603 | 4 |

### All 32 seed-level welfare outcomes

| Path | Seed | A original | B original | A equal | B equal | Original B-A | Equal B-A |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 | 1 | 10.2034 | 7.7729 | 10.2034 | 9.3993 | -2.4305 | -0.8041 |
| S1 | 2 | 10.0528 | 7.7545 | 10.0528 | 9.0964 | -2.2983 | -0.9563 |
| S1 | 3 | 10.4960 | 7.8595 | 10.4960 | 9.6082 | -2.6365 | -0.8878 |
| S1 | 4 | 10.4578 | 8.2438 | 10.4578 | 9.9317 | -2.2140 | -0.5261 |
| S1 | 5 | 10.2582 | 8.0477 | 10.2582 | 9.6047 | -2.2105 | -0.6535 |
| S1 | 6 | 10.3151 | 8.1296 | 10.3151 | 9.4645 | -2.1855 | -0.8506 |
| S1 | 7 | 9.9983 | 7.7746 | 9.9983 | 9.4602 | -2.2236 | -0.5381 |
| S1 | 8 | 10.2171 | 7.7866 | 10.2171 | 9.6997 | -2.4305 | -0.5174 |
| S2 | 1 | 9.9708 | 7.7206 | 9.9708 | 9.3470 | -2.2502 | -0.6238 |
| S2 | 2 | 9.8969 | 7.7037 | 9.8969 | 9.0456 | -2.1932 | -0.8512 |
| S2 | 3 | 10.2908 | 7.8305 | 10.2908 | 9.5792 | -2.4604 | -0.7117 |
| S2 | 4 | 10.3230 | 8.1953 | 10.3230 | 9.8832 | -2.1278 | -0.4398 |
| S2 | 5 | 10.1927 | 8.0203 | 10.1927 | 9.5773 | -2.1724 | -0.6154 |
| S2 | 6 | 10.1997 | 8.0956 | 10.1997 | 9.4305 | -2.1041 | -0.7692 |
| S2 | 7 | 9.8790 | 7.7389 | 9.8790 | 9.4245 | -2.1401 | -0.4545 |
| S2 | 8 | 10.1192 | 7.7507 | 10.1192 | 9.6638 | -2.3684 | -0.4553 |
| S3 | 1 | 9.8909 | 7.6881 | 9.8909 | 9.3144 | -2.2028 | -0.5765 |
| S3 | 2 | 9.6190 | 7.6489 | 9.6190 | 8.9901 | -1.9701 | -0.6289 |
| S3 | 3 | 10.1131 | 7.7971 | 10.1131 | 9.5458 | -2.3159 | -0.5673 |
| S3 | 4 | 10.0576 | 8.1422 | 10.0576 | 9.8096 | -1.9153 | -0.2479 |
| S3 | 5 | 9.8278 | 7.9173 | 9.8278 | 9.4730 | -1.9105 | -0.3548 |
| S3 | 6 | 10.0348 | 8.0431 | 10.0348 | 9.3776 | -1.9917 | -0.6572 |
| S3 | 7 | 9.4652 | 7.6987 | 9.4652 | 9.3838 | -1.7665 | -0.0814 |
| S3 | 8 | 9.6443 | 7.6727 | 9.6443 | 9.5852 | -1.9717 | -0.0591 |
| S4 | 1 | 9.5231 | 7.5228 | 9.5231 | 9.0895 | -2.0004 | -0.4337 |
| S4 | 2 | 9.2939 | 7.5697 | 9.2939 | 8.8763 | -1.7242 | -0.4176 |
| S4 | 3 | 9.4647 | 7.6786 | 9.4647 | 9.3934 | -1.7861 | -0.0713 |
| S4 | 4 | 9.3231 | 8.0342 | 9.3231 | 9.6793 | -1.2888 | 0.3562 |
| S4 | 5 | 9.1953 | 7.7657 | 9.1953 | 9.2886 | -1.4295 | 0.0934 |
| S4 | 6 | 9.6604 | 7.9142 | 9.6604 | 9.2259 | -1.7463 | -0.4346 |
| S4 | 7 | 8.9244 | 7.5526 | 8.9244 | 9.2355 | -1.3718 | 0.3111 |
| S4 | 8 | 8.7938 | 7.5686 | 8.7938 | 9.4497 | -1.2252 | 0.6559 |

## R3. Full individual-agent decision trace

Actor HH-0001, scenario S2, seed 1. All 52 weeks for Policy A original and Policy B equal delay. Every record has state transitions, action, budgets, displacement accumulation, shock flags, local welfare, peer influence, version, seed and provenance. Full records are supplied in CSV and JSONL files; this appendix prints selected core columns below.

| Policy | Week | Prior | Action | Next | Budget before | Budget after | Welfare |
|---|---:|---|---|---|---:|---:|---:|
| A_original | 1 | pending | take_possession | stable | 1442.43 | 1441.78 | 11.485 |
| A_original | 2 | stable | hold | stable | 1441.78 | 1441.13 | 11.785 |
| A_original | 3 | stable | hold | stable | 1441.13 | 1440.48 | 11.785 |
| A_original | 4 | stable | hold | stable | 1440.48 | 1439.83 | 11.785 |
| A_original | 5 | stable | hold | stable | 1439.83 | 1439.18 | 11.785 |
| A_original | 6 | stable | hold | stable | 1439.18 | 1438.53 | 11.785 |
| A_original | 7 | stable | hold | stable | 1438.53 | 1437.88 | 11.785 |
| A_original | 8 | stable | hold | stable | 1437.88 | 1437.23 | 9.82 |
| A_original | 9 | stable | hold | stable | 1437.23 | 1436.58 | 9.82 |
| A_original | 10 | stable | hold | stable | 1436.58 | 1435.93 | 9.82 |
| A_original | 11 | stable | hold | stable | 1435.93 | 1435.28 | 11.785 |
| A_original | 12 | stable | hold | stable | 1435.28 | 1434.63 | 9.82 |
| A_original | 13 | stable | hold | stable | 1434.63 | 1433.98 | 9.82 |
| A_original | 14 | stable | hold | stable | 1433.98 | 1433.33 | 11.785 |
| A_original | 15 | stable | hold | stable | 1433.33 | 1432.68 | 11.785 |
| A_original | 16 | stable | hold | stable | 1432.68 | 1432.03 | 11.785 |
| A_original | 17 | stable | hold | stable | 1432.03 | 1431.38 | 11.785 |
| A_original | 18 | stable | hold | stable | 1431.38 | 1430.73 | 11.785 |
| A_original | 19 | stable | hold | stable | 1430.73 | 1430.08 | 9.82 |
| A_original | 20 | stable | hold | stable | 1430.08 | 1429.43 | 9.82 |
| A_original | 21 | stable | hold | stable | 1429.43 | 1428.78 | 11.785 |
| A_original | 22 | stable | hold | stable | 1428.78 | 1428.13 | 11.785 |
| A_original | 23 | stable | hold | stable | 1428.13 | 1427.48 | 9.82 |
| A_original | 24 | stable | hold | stable | 1427.48 | 1426.83 | 11.785 |
| A_original | 25 | stable | hold | stable | 1426.83 | 1426.18 | 11.785 |
| A_original | 26 | stable | hold | stable | 1426.18 | 1425.53 | 9.82 |
| A_original | 27 | stable | retrofit_blocked_budget | stable | 1425.53 | 1424.88 | 9.82 |
| A_original | 28 | stable | hold | stable | 1424.88 | 1424.23 | 9.82 |
| A_original | 29 | stable | hold | stable | 1424.23 | 1423.58 | 11.785 |
| A_original | 30 | stable | hold | stable | 1423.58 | 1422.93 | 9.82 |
| A_original | 31 | stable | hold | stable | 1422.93 | 1422.28 | 11.785 |
| A_original | 32 | stable | hold | stable | 1422.28 | 1421.63 | 11.785 |
| A_original | 33 | stable | hold | stable | 1421.63 | 1420.98 | 9.82 |
| A_original | 34 | stable | hold | stable | 1420.98 | 1420.33 | 11.785 |
| A_original | 35 | stable | hold | stable | 1420.33 | 1419.68 | 9.82 |
| A_original | 36 | stable | hold | stable | 1419.68 | 1419.03 | 11.785 |
| A_original | 37 | stable | hold | stable | 1419.03 | 1418.38 | 9.82 |
| A_original | 38 | stable | hold | stable | 1418.38 | 1417.73 | 11.785 |
| A_original | 39 | stable | hold | stable | 1417.73 | 1417.08 | 11.785 |
| A_original | 40 | stable | hold | stable | 1417.08 | 1416.43 | 11.785 |
| A_original | 41 | stable | hold | stable | 1416.43 | 1415.78 | 11.785 |
| A_original | 42 | stable | hold | stable | 1415.78 | 1415.13 | 11.785 |
| A_original | 43 | stable | hold | stable | 1415.13 | 1414.48 | 11.785 |
| A_original | 44 | stable | hold | stable | 1414.48 | 1413.83 | 11.785 |
| A_original | 45 | stable | hold | stable | 1413.83 | 1413.18 | 11.785 |
| A_original | 46 | stable | hold | stable | 1413.18 | 1412.53 | 11.785 |
| A_original | 47 | stable | hold | stable | 1412.53 | 1411.88 | 11.785 |
| A_original | 48 | stable | hold | stable | 1411.88 | 1411.23 | 11.785 |
| A_original | 49 | stable | hold | stable | 1411.23 | 1410.58 | 11.785 |
| A_original | 50 | stable | hold | stable | 1410.58 | 1409.93 | 11.785 |
| A_original | 51 | stable | hold | stable | 1409.93 | 1409.28 | 9.82 |
| A_original | 52 | stable | hold | stable | 1409.28 | 1408.63 | 11.785 |
| B_equal_delay | 1 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.674 |
| B_equal_delay | 2 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 3 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 4 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 5 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 6 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 7 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 8 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 9 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 10 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 11 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 12 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 13 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 14 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 15 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 16 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 17 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 18 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 19 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 20 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 21 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 22 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 23 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 24 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 25 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 26 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 27 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 28 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 29 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 30 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 31 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 32 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 33 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 34 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 35 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 36 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 37 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 38 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 39 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 40 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 41 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 42 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 43 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 44 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 45 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 46 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 47 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 48 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 49 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 50 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |
| B_equal_delay | 51 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.188 |
| B_equal_delay | 52 | displaced | hold | displaced | 1922.43 | 1922.43 | 4.974 |

## R4. Limitations and interpretation

The B-A gap improved by 1.603 simulated welfare points overall but remained negative across all 32 paired observations on average. In S4 the mean B-A gap is approximately +0.007 and only 4/8 seeds favour B; there is no robust ranking reversal. The delay is a model parameter that also enters household acceptance utility, so this sensitivity measures the model-defined combination of waiting time and adoption response. It does not isolate construction timing from preferences.

The two scenarios differ in remaining fixed assumptions: initial material cost, government subsidy, protection and maintenance. Thus equal delays do not equalise budget constraints or procurement feasibility. Synthetic welfare is not validated against Aceh survey or disaster data. No inference about actual shelters is warranted. The earlier RRI formula double-counts displacement and is not used here.

## R5. Reproduction

From the extracted package root, run `python src/run_equal_delay.py`. It replays 32 A controls, asserts identical baseline welfare for each and executes 32 B equal-delay runs, producing seed-level results, summary and one compressed complete B trace. All referenced inputs and source files are in this package.
