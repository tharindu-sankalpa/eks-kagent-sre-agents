#!/usr/bin/env python3
"""Turns results/answers/*/sNN.json into results/summary/scenarios.md.

For each scenario: agent, state, wall-clock seconds (from the .txt written by
ask-agent.sh), number of tool calls (A2A history parts whose metadata marks
them as a function call), and the first line of the answer.
"""
import glob, json, pathlib, re

rows = []
seen = set()
for f in sorted(glob.glob("results/answers/*/s[0-9][0-9].events.jsonl")) + sorted(glob.glob("results/answers/*/s[0-9][0-9].json")):
    p = pathlib.Path(f)
    agent, sid = p.parent.name, p.name.split(".")[0]
    if (agent, sid) in seen:
        continue
    if f.endswith(".events.jsonl"):
        # streamed (message/stream): one JSON event per line
        events = [json.loads(l) for l in open(f) if l.strip()]
        if not events:
            continue
        seen.add((agent, sid))
        updates = [e["result"] for e in events if e.get("result", {}).get("kind") == "status-update"]
        state = updates[-1]["status"]["state"] if updates else events[-1].get("error", {}).get("message", "?")
        names = [part["data"]["name"] for u in updates for part in (u["status"].get("message") or {}).get("parts", [])
                 if part.get("kind") == "data" and (part.get("metadata") or {}).get("kagent_type") == "function_call"]
        r = {"history": []}
        calls = len(names)
    else:
        try:
            d = json.load(open(f))
        except json.JSONDecodeError:
            continue  # still running or empty
        seen.add((agent, sid))
        r = d.get("result", {})
        state = (r.get("status") or {}).get("state", d.get("error", {}).get("message", "?"))
        calls, names = 0, []
    for m in r.get("history", []) or []:
        for part in m.get("parts", []) or []:
            md = part.get("metadata") or {}
            if part.get("kind") == "data" and md.get("kagent_type") == "function_call":
                calls += 1
                names.append((part.get("data") or {}).get("name", "?"))
    if calls == 0:  # the BYO agent reports each tool call as a "call: name(args)" progress message instead
        for m in r.get("history", []) or []:
            if m.get("role") != "agent":
                continue
            for part in m.get("parts", []) or []:
                t = part.get("text") or ""
                if t.startswith("call: "):
                    calls += 1
                    names.append(t[6:].split("(")[0])
    tp = p.parent / f"{sid}.txt"
    txt = tp.read_text() if tp.exists() else ""
    q = re.search(r"^Q: (.*)$", txt, re.M)
    secs = re.search(r"\((\d+)s\)", txt)
    body = txt.split("\n\n", 1)[1].strip() if "\n\n" in txt else ""
    answer = body.splitlines()[0] if body else "(no answer text)"
    rows.append({"id": sid, "agent": agent, "state": state, "secs": int(secs.group(1)) if secs else None,
                 "calls": calls, "tools": sorted(set(names)), "question": q.group(1) if q else "", "first_line": answer[:140]})

out = ["| id | agent | state | s | tool calls | distinct tools | first line of answer |", "|---|---|---|---|---|---|---|"]
for r in rows:
    out.append(f"| {r['id']} | {r['agent']} | {r['state']} | {r['secs']} | {r['calls']} | {', '.join(r['tools'])} | {r['first_line'].replace('|', '/')} |")
pathlib.Path("results/summary").mkdir(parents=True, exist_ok=True)
pathlib.Path("results/summary/scenarios.md").write_text("\n".join(out) + "\n")
json.dump(rows, open("results/summary/scenarios.json", "w"), indent=1)
print("\n".join(out))
