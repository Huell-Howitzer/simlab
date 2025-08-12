Cool idea. Easiest way: let your issue YAML describe N runs and let any string field support tiny “brace expansion” + ${run} interpolation. Then expand to a per‑run parameter set before you submit your Slurm array.

Here’s a drop‑in Python helper you can call after you parse the issue body (works with {a,b,c}, {1..10}, {01..10}, {1..10..2}, mixes with suffixes/prefixes, cycles if lengths don’t match, and supports ${run}):

import re
from typing import List, Dict, Any
import yaml

_rng = re.compile(r"\{(-?\d+)\.\.(-?\d+)(?:\.\.(-?\d+))?\}")
_lst = re.compile(r"\{([^{}]+)\}")
_var = re.compile(r"\$\{(\w+)\}")

def _expand_braces_once(s: str):
    # numeric range {start..end[..step]}
    m = _rng.search(s)
    if m:
        start, end, step = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
        width = max(len(m.group(1).lstrip('-')), len(m.group(2).lstrip('-')))
        seq = []
        if step == 0:
            raise ValueError("Range step cannot be 0")
        if (end - start) * step < 0:
            step = -step
        i = start
        if step > 0:
            while i <= end:
                seq.append(f"{i:0{width}d}" if width > 1 else str(i))
                i += step
        else:
            while i >= end:
                seq.append(f"{i:0{width}d}" if width > 1 else str(i))
                i += step
        return seq, _rng.sub("{}", s, count=1)
    # list {a,b,c}
    m = _lst.search(s)
    if m:
        items = [part.strip() for part in m.group(1).split(",")]
        return items, _lst.sub("{}", s, count=1)
    return None, s

def brace_product(s: str) -> List[str]:
    # supports multiple brace groups: "foo{a,b}{1..3}.txt"
    parts = [s]
    while True:
        new_parts = []
        changed = False
        for p in parts:
            seq, templ = _expand_braces_once(p)
            if seq is None:
                new_parts.append(p)
            else:
                changed = True
                for item in seq:
                    new_parts.append(templ.format(item))
        parts = new_parts
        if not changed:
            break
    return parts

def interpolate_vars(s: str, env: Dict[str, Any]) -> str:
    def repl(m):
        key = m.group(1)
        return str(env.get(key, m.group(0)))
    return _var.sub(repl, s)

def expand_issue_yaml(yaml_text: str) -> List[Dict[str, Any]]:
    """
    Expects YAML like:
      runs: 10
      params:
        seed: "${run}"
        input_file: "{a,b,c,d,u,v,w,x,y,z}.txt"
        out: "out_{01..10}.dat"
        alpha: [0.1, 0.2]         # lists work too (cycle)
        mode: steady              # scalars replicate
    Returns a list of dicts, one per run (run = 1..runs).
    """
    cfg = yaml.safe_load(yaml_text)
    runs = int(cfg.get("runs") or cfg.get("n_runs") or 1)
    params = cfg.get("params", {})
    # Precompute each key -> list of values across runs
    expanded_columns: Dict[str, List[str]] = {}

    for key, val in params.items():
        # Normalize to list-of-run-values
        if isinstance(val, str):
            # First do brace expansion -> can yield many candidates.
            # If multiple groups, brace_product returns cartesian; if count != runs:
            # - if len == runs: index by run
            # - if len divides runs: cycle
            # - if len == 1: repeat
            # - else: cycle by default
            candidates = brace_product(val)
            if not candidates:
                candidates = [val]
            # Now per-run assign with ${run} interpolation afterwards
            col = []
            L = len(candidates)
            for r in range(1, runs + 1):
                chosen = candidates[(r - 1) % L]
                col.append(chosen)
            expanded_columns[key] = col
        elif isinstance(val, list):
            # cycle through list across runs
            col = []
            L = len(val)
            for r in range(1, runs + 1):
                chosen = val[(r - 1) % L]
                col.append(str(chosen))
            expanded_columns[key] = col
        else:
            # scalar: replicate
            expanded_columns[key] = [str(val)] * runs

    # Now assemble per-run dicts and apply ${run} etc.
    rows: List[Dict[str, Any]] = []
    for r in range(1, runs + 1):
        env = {"run": r, "RUN": r, "idx0": r - 1, "IDX0": r - 1}
        row = {}
        for k, col in expanded_columns.items():
            row[k] = interpolate_vars(col[r - 1], env)
        # default seed if not provided
        if "seed" not in row:
            row["seed"] = str(r)
        rows.append(row)
    return rows

Example use

Issue body YAML:

runs: 10
params:
  seed: "${run}"
  input_file: "{a,b,c,d,u,v,w,x,y,z}.txt"
  out: "result_{01..10}.nc"
  perturb: [low, high]    # cycles: low, high, low, ...

Call:

rows = expand_issue_yaml(issue_yaml_text)
# rows[0] -> run 1: {'seed':'1','input_file':'a.txt','out':'result_01.nc','perturb':'low'}
# rows[9] -> run 10: {'seed':'10','input_file':'z.txt','out':'result_10.nc','perturb':'high'}

Submitting as a Slurm array

Have your launcher write a small TSV/JSON and use --array:

# write TSV
with open("runs.tsv","w") as f:
    # header
    keys = list(rows[0].keys())
    f.write("\t".join(keys) + "\n")
    for r in rows:
        f.write("\t".join(str(r[k]) for k in keys) + "\n")

# submit
import subprocess
subprocess.run(["sbatch", "--array=0-{}".format(len(rows)-1), "job.sbatch"], check=True)

job.sbatch can read the line by $SLURM_ARRAY_TASK_ID:

#!/usr/bin/env bash
#SBATCH -J mc
#SBATCH -o logs/%A_%a.out
set -euo pipefail

ROW=$(( SLURM_ARRAY_TASK_ID + 1 ))   # skip header in TSV
IFS=$'\t' read -r -a KEYS < <(head -n1 runs.tsv)
IFS=$'\t' read -r -a VALS < <(sed -n "$((ROW+0))p" runs.tsv)

# export params as env vars
for i in "${!KEYS[@]}"; do
  k="${KEYS[$i]}"
  v="${VALS[$i]}"
  export "$k"="$v"
done

echo "Run $SLURM_ARRAY_JOB_ID.$SLURM_ARRAY_TASK_ID with seed=$seed input_file=$input_file out=$out perturb=$perturb"
# your command here, e.g.:
# srun ./simulate --seed "$seed" --in "$input_file" --out "$out" --perturb "$perturb"

Notes & niceties
	•	${run} (1-based) and ${idx0} (0-based) are available in any string.
	•	Brace lists + numeric ranges can be combined: foo_{A,B}{1..3}.bin → foo_A1.bin, foo_A2.bin, ....
	•	Length handling: if list/range length equals runs, it’s 1:1; otherwise it cycles (simple and practical). You can change that to “error if mismatched” if you prefer stricter behavior.
	•	To keep things YAML‑friendly, if you ever need a literal { or }, escape by wrapping the whole string in single quotes and doubling braces, e.g. 'use {{curly}} literally'.

If you want me to adapt this to your existing parser or switch the TSV to JSON/env‑file, say the word and I’ll tailor it.