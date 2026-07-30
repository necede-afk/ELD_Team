#!/usr/bin/env python3
"""
Batch-generate Do Now images for ELD 1,2 and ELD 3,4 using gpt-image-2.

RESUME-SAFE: skips any image that already exists on disk. Run it as many times as
you like — it only makes what is missing.

Usage
-----
    python generate_images.py                 # generate everything missing
    python generate_images.py --course ELD12  # one course only
    python generate_images.py --dry-run       # show what WOULD be made, cost nothing
    python generate_images.py --limit 5       # make 5 and stop (good first test)

Env
---
    OPENAI_API_KEY   required unless your Codex OAuth provides image access
"""

import argparse, base64, json, os, sys, time
from pathlib import Path

MODEL = "gpt-image-2"
SIZE = "1536x1024"          # 16:9-ish landscape
QUALITY = "high"
HERE = Path(__file__).parent
MANIFEST = HERE / "manifest.json"
STYLE = HERE / "style_prompt.txt"
OUT = {
    "ELD12": HERE / "ELD 1-2",
    "ELD34": HERE / "ELD 3-4",
}
LOG = HERE / "generation_log.jsonl"

PANEL_NOTE = (
    "\n\nIMPORTANT: this scene is deliberately MULTI-PANEL. Produce it as ONE single "
    "16:9 image divided into panels within that one frame — not as separate images, "
    "not as a grid of thumbnails. One artwork, internally divided."
)


def load():
    if not MANIFEST.exists():
        sys.exit(f"missing {MANIFEST}")
    if not STYLE.exists():
        sys.exit(f"missing {STYLE}")
    return json.loads(MANIFEST.read_text()), STYLE.read_text()


def log(rec):
    with LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", choices=["ELD12", "ELD34"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--sleep", type=float, default=1.5,
                    help="seconds between calls, to stay under rate limits")
    args = ap.parse_args()

    manifest, style = load()
    for d in OUT.values():
        d.mkdir(parents=True, exist_ok=True)

    todo, skipped = [], {"flagged": 0, "exists": 0, "course": 0}
    for e in manifest:
        if e.get("skip"):
            skipped["flagged"] += 1
            continue
        if args.course and e["course"] != args.course:
            skipped["course"] += 1
            continue
        if (OUT[e["course"]] / e["file"]).exists():
            skipped["exists"] += 1
            continue
        todo.append(e)

    if args.limit:
        todo = todo[: args.limit]

    print(f"\n  to generate : {len(todo)}")
    print(f"  already done: {skipped['exists']}")
    print(f"  excluded    : {skipped['flagged']}  (photos, text-bearing, reuses)")
    if args.course:
        print(f"  other course: {skipped['course']}")
    est = len(todo) * 0.19
    print(f"  est. cost   : up to ${est:.2f} at $0.19/image\n")

    if args.dry_run:
        for e in todo:
            tag = " [PANELS]" if e.get("panels") else ""
            print(f"    {e['file']}{tag}")
            print(f"        {e['scene'][:96]}")
        print(f"\n  DRY RUN — nothing generated.\n")
        return

    if not todo:
        print("  nothing to do.\n")
        return

    from openai import OpenAI
    client = OpenAI()

    made = failed = 0
    for i, e in enumerate(todo, 1):
        prompt = style + e["scene"]
        if e.get("panels"):
            prompt += PANEL_NOTE
        dest = OUT[e["course"]] / e["file"]
        print(f"  [{i}/{len(todo)}] {e['file']}", flush=True)

        for attempt in (1, 2, 3):
            try:
                r = client.images.generate(
                    model=MODEL, prompt=prompt, size=SIZE, quality=QUALITY, n=1
                )
                dest.write_bytes(base64.b64decode(r.data[0].b64_json))
                made += 1
                log({"file": e["file"], "ok": True, "attempt": attempt,
                     "panels": bool(e.get("panels"))})
                break
            except Exception as ex:
                if attempt == 3:
                    failed += 1
                    print(f"        FAILED: {ex}", flush=True)
                    log({"file": e["file"], "ok": False, "error": str(ex)})
                else:
                    wait = 5 * attempt
                    print(f"        retry in {wait}s — {ex}", flush=True)
                    time.sleep(wait)

        time.sleep(args.sleep)

    print(f"\n  made {made}   failed {failed}")
    print(f"  log: {LOG}\n")
    print("  NEXT: audit at FULL SIZE, not thumbnails.")
    print("  Lettering hides in card labels, book spines, posters, packaging.")
    print("  Delete any image with a letterform and re-run this script — it will")
    print("  regenerate only what is missing.\n")


if __name__ == "__main__":
    main()
