# -*- coding: utf-8 -*-
"""harness50 실행기 — Stage 1 (Gate 0) 소거 패스.

각 iNN_<slug>.py 는 SPEC(사전 예측·게이트·kill 규칙)을 정의하고 run_spec(SPEC) 을 부른다.
판정 규칙(사전 등록, 전 카드 공통):
  KILL    — hard 게이트 하나라도 실패 (처치 정의 불가·핵심 필드 커버리지 미달·검정력 대리 최저선 미달)
  PARTIAL — hard 통과, soft 게이트 실패 (검정력 한계·커버리지 경계) → Stage 2 는 설계 축소 조건부
  GO      — 전 게이트 통과 → Stage 2 (본 추정) 진행 자격
Stage 1 은 효과를 추정하지 않는다. 여기서의 KILL 은 "이 데이터로는 그 설계를 지탱할 수 없다"는 뜻이며,
데이터가 확장되면(PitchBook·Refinitiv) KILL 을 전부 재점검한다(idea-harness run 규칙).
"""
import csv
import datetime
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CORES = os.environ.get("P001_CORES", "/path/to/cores_v1")  # Crunchbase-derived parquet (licensed; see DATA_ACCESS.md)
os.environ.setdefault("HARNESS_OUT", os.path.join(HERE, "out"))
os.environ.setdefault("PROJECT_BASE", os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
from emit_contract import emit  # noqa: E402

_TABLES = ["organizations", "funding_rounds", "investments", "investors", "acquisitions", "ipos",
           "funds", "people", "jobs", "degrees", "events", "event_appearances",
           "investment_partners", "org_parents"]


class Ctx:
    """cores_v1 지연 로딩 캐시 — run_all 이 한 프로세스에서 50개 스펙을 돌릴 때 한 번만 읽는다."""
    _cache = {}

    def __getattr__(self, name):
        key = {"orgs": "organizations", "rounds": "funding_rounds", "inv": "investments",
               "acq": "acquisitions", "eapp": "event_appearances", "partners": "investment_partners",
               "orgpar": "org_parents"}.get(name, name)
        if key not in _TABLES:
            raise AttributeError(name)
        if key not in Ctx._cache:
            df = pd.read_parquet(os.path.join(CORES, key + ".parquet"))
            # pyarrow 가 날짜열을 date32/timestamp 로 추론하고, pandas 는 이를 object(datetime.date)
            # 로 돌려준다 — dtype 문자열로는 못 잡는다. 스펙은 ISO 문자열 사전순 비교를 전제하므로
            # 날짜 열을 이름 기준으로 문자열 정규화한다 (str(date) == 'YYYY-MM-DD').
            DATE_COLS = {"announced_on", "founded_on", "closed_on", "last_funding_on", "acquired_on",
                         "went_public_on", "started_on", "ended_on", "completed_on", "created_at"}
            for c in df.columns:
                dt = str(df[c].dtype)
                if c in DATE_COLS or "date" in dt or "timestamp" in dt:
                    df[c] = df[c].astype("string")
            Ctx._cache[key] = df
        return Ctx._cache[key]


CTX = Ctx()


def gate(name, value, req, hard=False, op=">="):
    if hasattr(value, "item"):          # numpy/pandas 스칼라 → JSON 직렬화 가능하게
        value = value.item()
    ok = (value >= req) if op == ">=" else (value <= req)
    return {"gate": name, "value": round(float(value), 4) if isinstance(value, float) else value,
            "req": req, "op": op, "hard": bool(hard), "passed": bool(ok)}


def power_grade(n_events, go=200, floor=50):
    """검정력 대리(사전 등록): 처치측 사전기간 사건 수. go 미만이면 soft-fail, floor 미만이면 hard-fail."""
    return [gate("power_events_hard", n_events, floor, hard=True),
            gate("power_events_soft", n_events, go, hard=False)]


def run_spec(spec):
    metrics, gates = spec["compute"](CTX)
    hard_fail = [g for g in gates if g["hard"] and not g["passed"]]
    soft_fail = [g for g in gates if not g["hard"] and not g["passed"]]
    status = "KILL" if hard_fail else ("PARTIAL" if soft_fail else "GO")
    fails = ", ".join(g["gate"] for g in hard_fail + soft_fail) or "all gates passed"
    verdict = f"stage1 {status}: {fails}"
    rec = emit(spec["id"], spec["question"], status,
               {"metrics": metrics, "gates": gates}, prediction=spec["prediction"],
               verdict=verdict, kill_met=bool(hard_fail), n=metrics.get("n_treated"),
               extra={"stage": 1, "feeds": spec["feeds"], "slug": spec["slug"]})
    _registry_row(spec, rec)
    return rec


def _registry_row(spec, rec):
    path = os.path.join(HERE, "registry.csv")
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["id"] != spec["id"]]
    rows.append({"id": spec["id"], "script": f"i{spec['id'][2:]}_{spec['slug']}.py",
                 "question": spec["question"], "prediction": spec["prediction"],
                 "status": rec["status"], "verdict": rec["verdict"], "n": rec.get("n") or "",
                 "out_json": f"out/{spec['id'].replace('-', '')}.json", "sha256_16": rec["sha256_16"],
                 "date": datetime.date.today().isoformat(), "feeds": spec["feeds"]})
    rows.sort(key=lambda r: r["id"])
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "script", "question", "prediction", "status",
                                          "verdict", "n", "out_json", "sha256_16", "date", "feeds"])
        w.writeheader()
        w.writerows(rows)
