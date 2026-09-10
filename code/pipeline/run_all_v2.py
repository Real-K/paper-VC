# -*- coding: utf-8 -*-
"""Re-run every P001 harness on sample_v2 (D067) in dependency order with parallel lanes. Logs: 07_analysis/out/logs_v2/<script>.log.
Dependencies: p001_14 ← P00104b, P00111 · p001_14b ← P00111 · p001_31 ← P00130 · p001_51 ← P00142, P00149 · p001_52 ← P00146 · exhibits (p001_09) after all.
Usage: python run_all_v2.py [lanes]"""
import glob
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(os.environ.get("P001_ARTIFACTS", os.path.join(HERE, "..", "..", "artifacts")), "logs_v2"); os.makedirs(LOG, exist_ok=True)
LANES = int(sys.argv[1]) if len(sys.argv) > 1 else 6
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
scripts = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "p001_*.py")))
skip = {"p001_09_exhibits.py", "p001_09b_assemble_tables.py", "p001_09c_ledger_refresh.py", "p001_09d_compose_v9.py", "p001_rescue_common.py", "p001_v6_common.py"}
scripts = [s for s in scripts if s not in skip]
DEPS = {"p001_14_tier2_robust.py": ["p001_04b_stacked_fix.py", "p001_11_e3_deal_level.py"], "p001_14b_join_sensitivity.py": ["p001_11_e3_deal_level.py"],
        "p001_31_gate_power.py": ["p001_30_terrain_decomp.py"], "p001_51_within_round_variants.py": ["p001_42_within_round_reup.py", "p001_49_coattribution_audit.py"],
        "p001_52_balance_maxt.py": ["p001_46_balance_rothstein.py"]}
# long jobs first so the lanes stay busy
LONG = ["p001_46_balance_rothstein.py", "p001_13_battery_joint.py", "p001_14_tier2_robust.py", "p001_14b_join_sensitivity.py", "p001_55_table3_fixed_horizon_ladder.py", "p001_11_e3_deal_level.py", "p001_60_review_reanalyses.py", "p001_51_within_round_variants.py", "p001_04b_stacked_fix.py", "p001_62_rank_accounting.py"]
order = [s for s in LONG if s in scripts] + [s for s in scripts if s not in LONG]
done, running, failed, t0 = set(), {}, [], time.time()


def ready(s): return all(d in done for d in DEPS.get(s, []))


pending = list(order)
while pending or running:
    for s, (p, st) in list(running.items()):
        rc = p.poll()
        if rc is not None:
            del running[s]; (done if rc == 0 else failed).add(s) if rc == 0 else failed.append(s)
            if rc == 0: done.add(s)
            print(f"[{time.time()-t0:7.0f}s] {'OK  ' if rc == 0 else 'FAIL'} {s} ({time.time()-st:.0f}s)", flush=True)
    while len(running) < LANES:
        nxt = next((s for s in pending if ready(s)), None)
        if nxt is None: break
        pending.remove(nxt)
        running[nxt] = (subprocess.Popen([sys.executable, nxt], cwd=HERE, env=env, stdout=open(os.path.join(LOG, nxt + ".log"), "w", encoding="utf-8"), stderr=subprocess.STDOUT), time.time())
        print(f"[{time.time()-t0:7.0f}s] START {nxt}", flush=True)
    if not running and pending and not any(ready(s) for s in pending):
        print("blocked:", pending); break
    time.sleep(5)
print(f"finished in {(time.time()-t0)/60:.1f} min · ok {len(done)} · failed {failed}")
