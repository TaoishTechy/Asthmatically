
"""
interface.py — Terminal interface with 10 novel prompting ideas.
Run: python3 interface.py
"""

import argparse, json, os, sys, readline
from core import AGIEngine

APP_DIR = os.path.join(os.path.dirname(__file__), "state")
MEM_PATH = os.path.join(APP_DIR, "memory.json")
REG_PATH = os.path.join(APP_DIR, "registry.json")
CFG_PATH = os.path.join(APP_DIR, "config.json")

NOVEL_MODES = [
    ("vantage", "VANTAGE teleport — swap perspective/role instantly."),
    ("praxis", "PRAXIS stack — queue concrete paradox-aware actions."),
    ("nemesis", "NEMESIS audit — stress-test with collapse pressure."),
    ("mirror", "MIMESIS mirror — reflect your style back at you."),
    ("refract", "REFRACT bend — translate across symbolic layers."),
    ("conduit", "CONDUIT link — open cross-thread transfer channel."),
    ("revelation", "REVELATION probe — convert anomaly to insight."),
    ("sigma", "SIGMAFRAME — maximize stability envelope."),
    ("genesis", "GENESIS seed — spawn a new goal/entity."),
    ("sstp", "SSTP transmit — boost signal across loops.")
]

HELP = """\
Type your prompt directly, or prefix with a mode command:
  :vantage  :praxis  :nemesis  :mirror  :refract
  :conduit  :revelation  :sigma  :genesis  :sstp

Other commands:
  :save         -> save snapshot ('time crystal') of state
  :load <id>    -> load snapshot id
  :mem          -> show memory path
  :modes        -> list modes
  :quit         -> exit
"""

def ensure_dirs():
    os.makedirs(APP_DIR, exist_ok=True)

def list_modes():
    print("\n== Modes ==")
    for k,desc in NOVEL_MODES:
        print(f"  :{k:<10} {desc}")
    print()

def main():
    ensure_dirs()
    engine = AGIEngine(MEM_PATH, REG_PATH, CFG_PATH)
    session = engine.mem.load().get("sessions", [])
    if session:
        session_id = session[-1]["id"]
    else:
        session_id = engine.start_session()

    crystals_dir = os.path.join(APP_DIR, "crystals")
    os.makedirs(crystals_dir, exist_ok=True)

    print("ProtoAGI Terminal — no training data, just memory/linguistics/adaptation.")
    print(HELP)
    list_modes()

    while True:
        try:
            line = input("› ")
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not line.strip():
            continue

        if line.strip() in (":quit",":exit"):
            print("bye")
            break
        if line.strip() == ":modes":
            list_modes()
            continue
        if line.strip() == ":mem":
            print(f"Memory file: {MEM_PATH}")
            continue
        if line.strip() == ":save":
            # Time crystal snapshot
            m = engine.mem.load()
            import uuid, datetime, shutil
            cid = str(uuid.uuid4())[:8]
            path = os.path.join(crystals_dir, f"{cid}.json")
            with open(path, "w") as f:
                json.dump(m, f, indent=2)
            print(f"Saved time crystal: {cid}")
            continue
        if line.startswith(":load "):
            cid = line.split(" ",1)[1].strip()
            path = os.path.join(crystals_dir, f"{cid}.json")
            if os.path.exists(path):
                with open(path) as f:
                    data = json.load(f)
                with open(MEM_PATH,"w") as f:
                    json.dump(data,f,indent=2)
                print(f"Loaded time crystal: {cid}")
            else:
                print("No such crystal id.")
            continue

        # Mode parsing
        mode = "default"
        if line.startswith(":"):
            parts = line.split(" ",1)
            m = parts[0][1:].strip().lower()
            mode_keys = [k for k,_ in NOVEL_MODES]
            if m in mode_keys:
                mode = m
                line = parts[1] if len(parts)>1 else ""
            else:
                print("Unknown mode. Use :modes to list.")
                continue

        result = engine.process(session_id, line, mode=mode)
        print(result["text"])
        # Brief debug toggle (pressing just '.')
        if line.strip()==".":
            print("\n--- explain ---")
            print(json.dumps(result["explain"], indent=2))

if __name__ == "__main__":
    main()
