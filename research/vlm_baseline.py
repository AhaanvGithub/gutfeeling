#!/usr/bin/env python3
"""Could a general vision LLM ("a GPT wrapper") do this? Head-to-head on the MHIST test split (977 tiles, 7-pathologist
majority labels), the same images the app's panel is reported on (balanced accuracy 0.888).

The LLM is Gemma-4 31B (instruction-tuned, multimodal) on NCSA Lumen, given each tile with a careful expert prompt that
states the WHO 2019 criteria, and asked for SSL or HP plus a confidence. Best effort: temperature 0, one call per tile;
an unparseable answer counts as wrong (and is reported). Results: docs/results/vlm_baseline.json (+ per-tile rows).

  python research/vlm_baseline.py [--workers 6] [--limit N]
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DEMHIST_DATA", ROOT / "data"))
OUT = ROOT / "docs/results/vlm_baseline.json"
MODEL = os.environ.get("VLM_MODEL", "gemma-4-31b-it")
PROMPT = """You are an expert gastrointestinal pathologist. This is one H&E field (about 0.5 mm wide, low power) from a
colon polyp. Decide: sessile serrated lesion (SSL) or hyperplastic polyp (HP).
WHO 2019: SSL shows at least one unequivocally architecturally distorted serrated crypt: dilation of the crypt base,
boot-, L- or inverted-T-shaped crypts, horizontal growth along the muscularis mucosae, serration reaching the crypt base.
HP shows straight crypts with narrow bases and serration limited to the upper part of the crypts.
Answer with JSON only: {"call": "SSL" or "HP", "confidence": 50-100}"""

ap = argparse.ArgumentParser()
ap.add_argument("--workers", type=int, default=6)
ap.add_argument("--limit", type=int, default=0)
args = ap.parse_args()

ann = pd.read_csv(DATA / "mhist/annotations.csv")
test = ann[ann.Partition == "test"].reset_index(drop=True)
if args.limit:
    test = test.sample(args.limit, random_state=0)
cli = OpenAI(api_key=os.environ["LUMEN_API_KEY"], base_url="https://lumen.ncsa.illinois.edu/v1")


def ask(row):
    b = base64.b64encode((DATA / "mhist/images" / row["Image Name"]).read_bytes()).decode()
    for attempt in range(3):
        try:
            r = cli.chat.completions.create(model=MODEL, temperature=0, max_tokens=60, messages=[{"role": "user", "content": [
                {"type": "text", "text": PROMPT}, {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b}}]}])
            txt = r.choices[0].message.content or ""
            m = re.search(r'"call"\s*:\s*"(SSL|HP|SSA)"', txt, re.I)
            call = {"SSA": "SSL"}.get(m.group(1).upper(), m.group(1).upper()) if m else None
            return {"image": row["Image Name"], "truth": "SSL" if row["Majority Vote Label"] == "SSA" else "HP",
                    "votes": int(row["Number of Annotators who Selected SSA (Out of 7)"]), "call": call, "raw": txt[:200]}
        except Exception as e:
            time.sleep(2 + 3 * attempt)
            err = type(e).__name__
    return {"image": row["Image Name"], "truth": "SSL" if row["Majority Vote Label"] == "SSA" else "HP", "call": None, "raw": f"error {err}"}


t0 = time.time()
rows = []
with ThreadPoolExecutor(args.workers) as ex:
    for k, r in enumerate(ex.map(ask, [r for _, r in test.iterrows()]), 1):
        rows.append(r)
        if k % 50 == 0:
            print(f"{k}/{len(test)} ({time.time() - t0:.0f} s)", flush=True)
d = pd.DataFrame(rows)
ssl, hp = d[d.truth == "SSL"], d[d.truth == "HP"]
sens, spec = (ssl.call == "SSL").mean(), (hp.call == "HP").mean()
res = {"model": MODEL, "tiles": len(d), "unparsed": int(d.call.isna().sum()),
       "called_SSL_share": round(float((d.call == "SSL").mean()), 3),
       "SSL_caught": round(float(sens), 3), "HP_cleared": round(float(spec), 3),
       "balanced_accuracy": round(float((sens + spec) / 2), 3), "accuracy": round(float((d.call == d.truth).mean()), 3),
       "for_comparison": {"app_panel_test_balanced_accuracy": 0.888, "chance": 0.5},
       "seconds": round(time.time() - t0)}
OUT.write_text(json.dumps(res, indent=1))
OUT.with_name("vlm_baseline_rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
print(json.dumps(res, indent=1))
