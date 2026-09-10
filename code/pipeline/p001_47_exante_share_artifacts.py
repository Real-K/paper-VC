# -*- coding: utf-8 -*-
"""p001_47 — R4 식별 재확인이 요구한 세 개의 소형 산출물 (본문이 인용하나 JSON 에 없던 수치)

[왜] R4 ident.md (2) 항목 5·8: (a) "사전기 딜의 약 절반이 순위 시점 이후 실현" — 36개월 창이 CUT 뒤에 닫히는 딜 비중을 산출물로;
 (b) 고정지평 Mundlak 의 between 계수가 회사평균 조정성과(fm_adj)를 따로 넣지 않았다 — 회사평균 terrain 과 fm_adj 의 상관을 공개;
 (c) 표본 파트너 중 회사 내 유일 파트너(singleton) 수 — between 항에만 기여.
[구성] P001-33 A 조합·P001-38 패널과 동일(exit3, 사전 ≤ CUT, 사후 ≤ END_FON, n≥5).
[사전 예측] (a) 패널 딜 기준 창 미완결 0.45–0.49 · 결과 미확정(exit3=0 & 미완결) 0.42–0.46 · 전 사전기 딜 0.47–0.50 (심판 계산 46.81/44.20/48.67)
 (b) |corr| < 0.10 (심판 0.026) (c) singleton 500–560 / 2,017.
[판정] 산출물 스크립트 — status OK.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, CUT, END_FON, TC, add_firm_means, add_post, add_tenure, emit, first_deal_dates, load_deals, log,
                                partner_pre)

OUT = {}
dn = load_deals(with_exit_dt=True)
P, h = partner_pre(dn, "exit3")
P = add_post(P, dn, "exit3", end=END_FON)
P = add_tenure(P, first=first_deal_dates())
P = add_firm_means(P, TC + ["terrain", "adj"])
hp = h[h["partner_uuid"].isin(P["partner_uuid"])]
win_open = (hp["dt"] + pd.Timedelta(days=1095)) > CUT
undet = win_open & (hp["exit3"] == 0)
pre_all = dn[dn["dt"] <= CUT]
OUT["A_exante_share"] = {"panel_deals": int(len(hp)), "share_window_closes_after_cut_panel": round(float(win_open.mean()), 4),
                         "share_outcome_undetermined_at_cut_panel": round(float(undet.mean()), 4),
                         "share_window_closes_after_cut_all_pre": round(float(((pre_all["dt"] + pd.Timedelta(days=1095)) > CUT).mean()), 4),
                         "share_72m_window_closes_after_cut_all_pre": round(float(((pre_all["dt"] + pd.Timedelta(days=365 * 6)) > CUT).mean()), 4)}
pp_ = P.dropna(subset=["post_adj"])
OUT["B_firm_means"] = {"corr_fm_terrain_fm_adj_postsample": round(float(pp_[["fm_terrain", "fm_adj"]].corr().iloc[0, 1]), 4),
                       "corr_fm_terrain_fm_adj_all": round(float(P[["fm_terrain", "fm_adj"]].corr().iloc[0, 1]), 4)}
OUT["C_singletons"] = {"n_post_partners": int(len(pp_)), "n_singleton_at_firm": int((pp_["fm_k"] == 1).sum()), "share_singleton": round(float((pp_["fm_k"] == 1).mean()), 4),
                       "n_partners_in_multi_partner_firms": int((pp_["fm_k"] >= 2).sum())}
log(f"[A] 창 미완결 비중 패널 {OUT['A_exante_share']['share_window_closes_after_cut_panel']:.4f} · 미확정 {OUT['A_exante_share']['share_outcome_undetermined_at_cut_panel']:.4f} · 전 사전기 {OUT['A_exante_share']['share_window_closes_after_cut_all_pre']:.4f} · 72m {OUT['A_exante_share']['share_72m_window_closes_after_cut_all_pre']:.4f}")
log(f"[B] corr(fm_terrain, fm_adj) {OUT['B_firm_means']['corr_fm_terrain_fm_adj_postsample']:+.4f} | [C] singleton {OUT['C_singletons']['n_singleton_at_firm']}/{OUT['C_singletons']['n_post_partners']} ({OUT['C_singletons']['share_singleton']:.3f})")
a, b, c = OUT["A_exante_share"], OUT["B_firm_means"], OUT["C_singletons"]
pred = {"A_panel_0.45_0.49": 0.45 <= a["share_window_closes_after_cut_panel"] <= 0.49, "A_undet_0.42_0.46": 0.42 <= a["share_outcome_undetermined_at_cut_panel"] <= 0.46,
        "B_abs_corr_lt_0.10": abs(b["corr_fm_terrain_fm_adj_postsample"]) < 0.10, "C_singletons_500_560": 500 <= c["n_singleton_at_firm"] <= 560}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
emit("P001-47", "R4 소형 산출물: 사전기 딜의 순위 후 실현 비중 · 회사평균 terrain–adj 상관 · 단독 파트너 수", "OK", OUT,
     prediction="패널 창 미완결 0.45–0.49; 미확정 0.42–0.46; |corr|<0.10; singleton 500–560",
     verdict=(f"창 미완결(패널) {a['share_window_closes_after_cut_panel']:.3f} · 미확정 {a['share_outcome_undetermined_at_cut_panel']:.3f} · 전 사전기 {a['share_window_closes_after_cut_all_pre']:.3f} | "
              f"corr(fm_terrain, fm_adj) {b['corr_fm_terrain_fm_adj_postsample']:+.3f} | singleton {c['n_singleton_at_firm']}/{c['n_post_partners']} (예측 적중 {sum(pred.values())}/{len(pred)})"),
     kill_met=False, n=int(len(hp)), extra={"stage": 7, "feeds": "R4 ident (2) 항목 5·8", "slug": "exante_share_artifacts", "builds_on": "P001-33/38", "common_sha256_16": COMMON_SHA})
log("done")
