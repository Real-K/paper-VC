# Artifact manifest

73 aggregate result files in `artifacts/`. `sha256_16` is the first 16 hex digits of the file's SHA-256; `ledger_rows` counts the rows of `CLAIMS_LEDGER.csv` that cite the file; `read_by_exhibit_generator` marks the files `code/build/p001_09_exhibits.py` reads. Titles are in Korean (the project's working language); the paper's exhibits are in English.

| file | sha256_16 | bytes | id | status | generating script | ledger rows | exhibits | title |
|---|---|---|---|---|---|---|---|---|
| P00100.json | `fd78c549688e967d` | 255 | P001-00 | OK | `06_code/p001_00_sample_counts.py` | 0 | yes | 정본 표본 집계 카운트 (Table 1 입력) |
| P00101.json | `596cc7a58fb1551f` | 1,595 | P001-01 | PARTIAL | `p001_01_gmwx_staircase.py` | 1 |  | GMWX 계단식 — 가법 통제 vs 완전 셀 (H7, NA+EU) |
| P00101b.json | `46adaeba5265ca3b` | 1,415 | P001-01b | PARTIAL | `p001_01b_headline_staircase.py` | 0 |  | 헤드라인 계단식 — ff 딜 exit_ever 셀 사다리 (E2 전시물, NA+EU) |
| P00102.json | `d381c4b4f7022ac5` | 1,641 | P001-02 | GO | `p001_02_decomposition_region.py` | 4 | yes | 3층 분해 확정 + 지역 moderator + 매개 경로 (H8·X5, NA+EU) |
| P00103.json | `7a6973625a88a11f` | 2,049 | P001-03 | GO | `p001_03_adjudication_naeu.py` | 2 | yes | 판별 배터리 확정 + MDE 표 (E2, NA+EU 스테이지 셀) |
| P00104.json | `fc38a380d4543b3e` | 2,080 | P001-04 | PARTIAL | `p001_04_stacked_event.py` | 0 |  | 재가중 스택 이벤트 스터디 — E3 승격 시도, 수리 사다리 (H9) |
| P00104b.json | `54c5c4a1801a3aae` | 2,080 | P001-04b | PARTIAL | `p001_04b_stacked_fix.py` | 3 | yes | 재가중 스택 이벤트 스터디 — E3 승격 시도, 수리 사다리 (H9) |
| P00105.json | `1a0f21f1193285ee` | 1,350 | P001-05 | GO | `p001_05_trackrecord.py` | 2 | yes | 귀결 A — 트랙레코드 랭킹 왜곡: 원시 vs 배치조정 (NA+EU) |
| P00106.json | `c25cdd54a368f2c9` | 1,687 | P001-06 | GO | `p001_06_capital_stage.py` | 3 | yes | 귀결 B — 여성 창업자 자본의 단계 구조 (fp 채널의 단계별 소멸, NA+EU) |
| P00107.json | `aad08ff4a13d3329` | 2,627 | P001-07 | PARTIAL | `p001_07_robustness_grid.py` | 1 | yes | 강건성 격자 — 측정·표본·창·추론 축 (W4) |
| P00108.json | `ccc40dec0c37de7f` | 2,227 | P001-08 | PARTIAL | `p001_08_measurement_diags.py` | 3 | yes | 측정 진단 — 귀속 선택·결측 선택·드리프트·세분 Becker (W4) |
| P00110.json | `042ce11827ad6e9a` | 2,525 | P001-10 | GO | `p001_10_gap_ladder.py` | 4 | yes | 원 격차 위치 정본 사다리 — 지역×셀 (D012, Table 3 유일 소스) |
| P00111.json | `968361cc2b3e7dae` | 1,546 | P001-11 | PARTIAL | `p001_11_e3_deal_level.py` | 5 | yes | E3 딜 수준 스택 회귀 — 정보 손실 제거 (Track D, P-1) |
| P00112.json | `497e4075e8798bda` | 2,432 | P001-12 | GO | `p001_12_covadj_hazard.py` | 6 | yes | E2 공변량 조정 배터리 + 이산시간 해저드 (Track D, P-2·P-3) |
| P00113.json | `28e46e8144c69d6d` | 1,878 | P001-13 | PARTIAL | `p001_13_battery_joint.py` | 1 | yes | 판별 배터리 결합 — 지수 등가·IU-TOST·Romano-Wolf (Track D, P-4) |
| P00114.json | `0073914a6985a1b0` | 1,946 | P001-14 | GO | `p001_14_tier2_robust.py` | 3 | yes | 순서 불변 분해 + E2 순열 + E3 감도 곡선 (Track D, Tier 2) |
| P00114b.json | `12de5b472df050f3` | 1,994 | P001-14b | GO | `p001_14b_join_sensitivity.py` | 1 | yes | 순서 불변 분해 + E2 순열 + E3 감도 곡선 (Track D, Tier 2) |
| P00115.json | `3d748afd7bf4c7b3` | 1,813 | P001-15 | PARTIAL | `p001_15_gmwx_staircase_ff.py` | 1 | yes | 가법 통제 vs 완전 셀 — ff 딜 계단식 (Track C-②, R8) |
| P00116.json | `4d7f25fb0e9f2a33` | 1,294 | P001-16 | PARTIAL | `p001_16_meas_diags2.py` | 2 | yes | 딜 수준 귀속 진단 + 스테이지 라벨 품질 (Track C-④·⑥) |
| P00117.json | `06ea3031a3754531` | 1,029 | P001-17 | GO | `p001_17_ladder_reweight.py` | 2 | yes | Table 8 판정가능성 재가중 + 다수-여성 (Track C-⑤) |
| P00118.json | `56daee7618a4544f` | 1,058 | P001-18 | PARTIAL | `p001_18_career.py` | 0 |  | 커리어 검정 — 원시 vs 조정 랭크의 미래 딜플로우 가격 반영 (Track C-⑦) |
| P00118b.json | `333be5cff39853f2` | 1,074 | P001-18b | PARTIAL | `p001_18b_career_fix.py` | 2 | yes | 커리어 검정 — 원시 vs 조정 랭크의 미래 딜플로우 가격 반영 (Track C-⑦) |
| P00119.json | `c7898050e6fffe79` | 1,362 | P001-19 | GO | `p001_19_ss_row.py` | 4 | yes | Snellman–Solal 회사 간 행 — 리드 투자자 성별과 후속 조달 (Track C-③) |
| P00120.json | `58e2654c80962554` | 4,011 | P001-20 | PARTIAL | `p001_20_period_split.py` | 0 |  | 격차의 시대성 — 2000년대 vs 2010년대 코호트 (GMWX 비재현 규명) |
| P00121.json | `891452118822b55d` | 1,831 | P001-21 | PARTIAL | `p001_21_succession.py` | 0 |  | 승계 검정 — 이탈 후 채널을 누가 이어받는가 (§5 메커니즘) |
| P00121b.json | `c13c7e8cdbaf0f88` | 1,828 | P001-21b | PARTIAL | `p001_21b_succession_fix.py` | 0 |  | 승계 검정 — 이탈 후 채널을 누가 이어받는가 (§5 메커니즘) |
| P00122.json | `4a6d929306ba14ef` | 1,614 | P001-22 | PARTIAL | `p001_22_external_market.py` | 0 |  | 외부 시장 검정 — 이동·스핀아웃이 원시 vs 조정 랭크를 따르는가 |
| P00123.json | `2a9fcaa02e6ea2ca` | 4,213 | P001-23 | PARTIAL | `p001_23_audit_p22.py` | 2 | yes | P001-22 사양 전수감사 (경마 공선성·재모수화·표본외 예측력) + LP 측 검정 |
| P00124.json | `5f2fc237011a91f8` | 2,228 | P001-24 | GO | `p001_24_ss_rerun_cox.py` | 1 | yes | 주장 ③ S&S 대조 필수 재실행 — 여성전용 리드·첫라운드·US·Seed/A·2010-18·Cox |
| P00125.json | `40658a448f296552` | 3,340 | P001-25 | PARTIAL | `p001_25_wedge_decisive.py` | 6 | yes | ① 결정 검정 — wedge 가 장래성과 미예측 & 평가자 보상(결합 RI) |
| P00126.json | `00e0299354b41bcb` | 2,107 | P001-26 | GO | `p001_26_wedge_gender.py` | 2 | yes | wedge 예측력의 성별 함의 — 원고 프레임 확정 전 필수 검정 |
| P00127.json | `1915bd600b324d5d` | 3,505 | P001-27 | GO | `p001_27_loo_cellmean.py` | 2 | yes | 셀평균 잡음 검정 — leave-one-out 벤치마크 하에서 β_raw/adj 가 남는가 |
| P00128.json | `41ab07d4c09025ed` | 2,279 | P001-28 | PARTIAL | `p001_28_selection_terrain.py` | 4 | yes | 리뷰어 선제 검정 — 사후기 관측 선택(IPW) · 무조건 terrain · 레벨 항등 |
| P00129.json | `5aedeef302358a5e` | 3,975 | P001-29 | GO | `p001_29_overlap_stage.py` | 7 | yes | 리뷰어 선제 검정 II — 기업 중복 제외 · 단계 집중 통제 · 단위 병기 |
| P00130.json | `8448393b71e21368` | 6,391 | P001-30 | KILL | `p001_30_terrain_decomp.py` | 13 | yes | R2 결정 검정 — terrain 분해(빈티지/단계/섹터) · 연공 · 회사 FE · 고정지평 · leave-partner-out |
| P00131.json | `7b04e7440b85646e` | 6,253 | P001-31 | OK | `p001_31_gate_power.py` | 5 | yes | R2 게이트 검정력 진단 — MDE · within-firm 분산 비중 · 성분 다중성 |
| P00132.json | `239db3573830e944` | 4,826 | P001-32 | PARTIAL | `p001_32_firm_between_within.py` | 5 | yes | 회사 교란 between/within 분해 (Mundlak) + Hausman 형 대비 |
| P00133.json | `95b5d32637e56d6f` | 23,461 | P001-33 | GO | `p001_33_fixed_horizon_exit.py` | 14 | yes | 고정지평(출구 기반 exit3/exit6) 에서의 구성 성분 → 장래 셀 내 성과 (+회사 FE·새 기업·leave-company-out) |
| P00134.json | `4b0549d69e1ab70e` | 9,186 | P001-34 | PARTIAL | `p001_34_deal_rolling_fe.py` | 10 | yes | 딜 수준 롤링 구성 → 고정지평 셀 내 잔차: 회사×연 FE · 파트너 FE 사다리 |
| P00135.json | `29b36abdba83d77e` | 6,853 | P001-35 | OK | `p001_35_terrain_reliability.py` | 5 | yes | terrain 성분 반분 신뢰도 · 감쇠 보정 IV |
| P00136.json | `64e83ce88178bd26` | 6,317 | P001-36 | OK | `p001_36_gender_components.py` | 6 | yes | 성별 × terrain 성분 — 기울기 위치와 함의 상쇄량의 성분별 CI |
| P00137.json | `83491782eb294908` | 15,973 | P001-37 | PARTIAL | `p001_37_lp_components.py` | 4 | yes | Panel C 재검 — LP·시장 결과 ← terrain 성분 + late_sh |
| P00138.json | `883df60dd917e348` | 18,787 | P001-38 | OK | `p001_38_fixed_horizon_recheck.py` | 27 | yes | R3 결정 검정(파트너 수준, 고정 출구지평): 단계별 기저율 · Mundlak · 성별 함의 · ex-ante 창 · 중복만 · IPW · days≥0 · 표준화 · 반분 |
| P00139.json | `00c8ade4e694cb59` | 18,693 | P001-39 | OK | `p001_39_jobs_tenure_rank.py` | 12 | yes | CP-1: jobs 합류일·직함으로 재직연차·직급 직접 측정 — 개방·고정지평 재추정, 성별 격차, 관측 선택 |
| P00140.json | `d02d3c29a53a40b6` | 6,076 | P001-40 | OK | `p001_40_identifying_cells_audit.py` | 21 | yes | P2: 헤드라인의 식별 변이(혼합 셀·딜) · 동료 가용성 · 잭나이프 · 셀 내 재배정 위약 |
| P00141.json | `56274e6f0d4f857d` | 5,952 | P001-41 | OK | `p001_41_deal_rolling_no_adjpr.py` | 4 | yes | 딜 수준 회사×연 FE — 파트너 사전 잔차(adj_pr) 통제 유·무 병기 (R3 R-9) |
| P00142.json | `cdf11f861aacc062` | 11,069 | P001-42 | GO | `p001_42_within_round_reup.py` | 14 | yes | P1: 라운드 내 투자자 수준 결과 — 재참여·재귀속·리드, 혼성 신디케이트 |
| P00143.json | `adfe6917b1aafcdf` | 6,473 | P001-43 | GO | `p001_43_movers_assignment.py` | 10 | yes | P3: 이동자 — 파트너 구성 변화 ← 회사(파트너 제외) 구성 변화; 미래 회사·위약 이동·방향 위약 |
| P00144.json | `a8583d2b9c87d1fa` | 11,579 | P001-44 | PARTIAL | `p001_44_absence_spells.py` | 11 | yes | P4: 부재 스펠 — 동료 ff 비중 ← 파트너 부재(18/24/36m), 여성−남성 차, 기록·규모 위약, 사전추세 |
| P00145.json | `c4bfba4dfe109792` | 7,288 | P001-45 | OK | `p001_45_ladder_pipeline.py` | 17 | yes | P5: 금융 사다리 파이프라인 — 기업 소모 · 회사 후속 참여 · 파트너 재귀속 · 신규 진입 구성 (기술 통계) |
| P00146.json | `e919ec5f18cf7236` | 14,344 | P001-46 | OK | `p001_46_balance_rothstein.py` | 18 | yes | P8: 헤드라인 셀 내 사전 배정 공변량 균형 검정 (Rothstein 유사물) — 결합 순열 p · 크기 보정 · 양성 대조 · MDE |
| P00147.json | `2759b5e0bbd2831c` | 1,596 | P001-47 | OK | `p001_47_exante_share_artifacts.py` | 3 | yes | R4 소형 산출물: 사전기 딜의 순위 후 실현 비중 · 회사평균 terrain–adj 상관 · 단독 파트너 수 |
| P00148.json | `964d8d869344c472` | 12,798 | P001-48 | OK | `p001_48_region_split.py` | 21 | yes | 지역 분할 로버스트니스: 미국 · NA(미국+캐나다) · 유럽 — 격차 사다리·판별 마진·고정지평 구성 계수 |
| P00149.json | `ed3732b839805be3` | 4,763 | P001-49 | OK | `p001_49_coattribution_audit.py` | 25 | yes | 동료 비교의 식별 기반: 공동귀속(단일 라운드) 셀 비중 · 결과 분산이 있는 셀 · 희석 · 다중 라운드 셀만의 격차 |
| P00150.json | `6d49f4f25e6ecda0` | 3,166 | P001-50 | OK | `p001_50_hazard_identification.py` | 10 | yes | Table 4 해저드의 식별 변이: 공동귀속 셀 비중·결과 변이·희석, 다중 라운드 셀만의 해저드 격차 |
| P00151.json | `c1b43bb875e12291` | 18,346 | P001-51 | PARTIAL | `p001_51_within_round_variants.py` | 29 | yes | R5 A-1: 라운드 내 재참여 설계의 변형 배터리 — 처치 정의·사전 투자자 통제·두-방향 FE·투자자 군집·양성 대조·추정 대상 |
| P00152.json | `b1eb177af6b86487` | 37,791 | P001-52 | OK | `p001_52_balance_maxt.py` | 47 | yes | R5 E-1/E-2 + R5-4: 균형검정 재통계 — max-/t/ 결합 순열 · 다중 라운드 셀 위 비희석 균형(sd 단위·MDE) · 희석 항등식 · Table 10 A 희석 |
| P00154.json | `6e37dc4c3924a773` | 12,417 | P001-54 | GO | `p001_54_within_partner_outcome.py` | 16 | yes | R5-1: 파트너 내 결과 검정 — 같은 파트너의 FF vs 비FF 딜의 시장 벤치마크 잔차, 파트너 성별 교차항 (파트너 FE·딜 통제·파트너 군집) |
| P00155.json | `f59838d12321ed1b` | 13,987 | P001-55 | OK | `p001_55_table3_fixed_horizon_ladder.py` | 49 | yes | R5-3: Table 3 고정 36m 지평(exit3, 딜 ≤2020-10)·달력 거칠기 사다리·다중 라운드 셀 추정량·딜 수준 처치 코딩 |
| P00156.json | `b0fe0c178207570c` | 12,397 | P001-56 | OK | `p001_56_within_round_v2.py` | 18 | yes | R5-5: 라운드 내 재참여 v2 — 리드 플래그 합집합·파트너 연공·글로벌+24m 창·전남성 위약 풀·재참여↔출구 보정 (설계의 CB 천장) |
| P00157.json | `2b8f351c3ceedc95` | 6,927 | P001-57 | OK | `p001_57_within_partner_horizon.py` | 5 |  | P001-54 후속: 파트너 내 결과 검정의 결과 구성물 분해 (같은 창에서 exit3·exit6·exit_ever·36m 이후 출구·fon) |
| P00158.json | `ff8e6e5457c756da` | 24,922 | P001-58 | OK | `p001_58_public_sources_controls.py` | 21 | yes | 공개 소스 변수 투입: 라운드 내 펀드 통제(CB funds·Form D T1) · §6 between 분해 · 특허 균형/통제(PatentsView v2) |
| P00159.json | `47f598292efc2350` | 15,149 | P001-59 | OK | `p001_59_within_partner_extensions.py` | 13 | yes | R6 ident 후속: 파트너 내 검정 확장(빈티지×지평·이탈 상태·회사 군집·LOO·IPO/인수·Holm·국가 벤치마크·선택) + 라운드 내 밴드 2,000회 |
| I73.json | `779a52a0c69980f5` | 2,221 | I-73 | GO | `i73_gender_screening.py` | 3 |  | 여성 파트너×여성 창업자 — 호의 vs 선별 판별 (K-3 본추정) |
| I74.json | `82bcddf31b7964b6` | 1,334 | I-74 | PARTIAL | `i74_gender_gates.py` | 2 |  | 동류교배 게이트 — 섹터·국가 구성 교란과 측정 강건성 (K-3) |
| I75.json | `070ca71325c5eef0` | 1,539 | I-75 | GO | `i75_gender_adjud_cells.py` | 0 |  | 판별의 섹터 셀 재추정 — 선별 vs 호의 (K-3 최종 게이트) |
| I76.json | `1e06d779177f2c7a` | 1,662 | I-76 | PARTIAL | `i76_gender_shock.py` | 1 |  | 충격 레이어 — 여성 파트너 깨끗한 영입·이탈과 여성 창업 신규 딜 (K-3 인과층) |
| I77.json | `9ef446e1aca5678f` | 1,421 | I-77 | PARTIAL | `i77_exit_power_sample.py` | 0 |  | 출구 판별 검정력 보강 — 표본 소급 2005+ (K-3 power-rescue 레버 B) |
| I78.json | `9d8d964e10bf0636` | 1,931 | I-78 | PARTIAL | `i78_exit_battery.py` | 2 |  | 출구 판별 결과변수 품질 배터리 (K-3 power-rescue 레버 C) |
| I79.json | `5858f25bacf48b13` | 1,371 | I-79 | GO | `i79_shock_joint.py` | 1 |  | 충격 레이어 결합 검정 + 추세 조정 (K-3 인과층 최종) |
| I80.json | `7274b607ab9eef28` | 1,510 | I-80 | GO | `i80_stage_control.py` | 3 |  | 스테이지 구성 교란 점검 — exit-ever 열위 판별 (K-3 판별 최종) |
| I81.json | `8757f43b5457031e` | 2,151 | I-81 | GO | `i81_stage_mechanism.py` | 2 |  | 스테이지 skew 메커니즘 배터리 — 창업자 경로·연차·동학·Becker (P001 2막) |
| I82.json | `651c511d39ebf22f` | 1,429 | I-82 | PARTIAL | `i82_e3_repairs.py` | 1 |  | E3 심판 수리 — 추세 조정 결합 CI + 동료-딜 분해 (P001 동결 전) |

Also in `artifacts/`: `CLAIMS_LEDGER.csv` (the claim-level ledger, 542 rows), `run_log.csv` (one row per harness run: script, sha256_16 of the script, inputs, output, verdict), `sample_manifest.yaml` (row count and SHA-256 of the frozen analysis file, which is not redistributed).
