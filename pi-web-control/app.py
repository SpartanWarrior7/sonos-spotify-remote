from fastapi import FastAPI, HTTPException
import subprocess
import sys
from pathlib import Path
from fastapi.responses import FileResponse

app = FastAPI()

# Path to the target file and main script
SCRIPT_DIR = Path(__file__).parent
TARGET_FILE = SCRIPT_DIR / "current_target.txt"
SONOS_SCRIPT = SCRIPT_DIR.parent / "sonos_web_actions.py"

# Allowed actions and zones
ACTIONS = ["playpause", "next", "volume_up", "volume_down", "play_liked", "play_christmas"]
ZONES = ["luke", "dlk", "family"]

def get_current_target():
    if TARGET_FILE.exists():
        return TARGET_FILE.read_text().strip()
    return "luke"

def set_current_target(target: str):
    TARGET_FILE.write_text(target)

@app.get("/")
def home_page():
    return FileResponse("index.html")

@app.get("/get_target")
def get_target():
    return {"target": get_current_target()}

@app.get("/set_target")
def set_target(zones: str):
    # zones is comma-separated, e.g. "luke,dlk,family"
    selected = [z.strip() for z in zones.split(",") if z.strip() in ZONES]

    if not selected:
        raise HTTPException(status_code=400, detail="No valid zones selected")

    target = ",".join(selected)
    set_current_target(target)

    return {
        "exit_code": 0,
        "output": f"Target set to: {target}\n",
        "error": "",
        "target": target
    }

@app.get("/run/sonos_{action}")
def run_sonos_action(action: str):
    if action not in ACTIONS:
        raise HTTPException(status_code=404, detail=f"Unknown action: {action}")

    target = get_current_target()

    result = subprocess.run(
        [sys.executable, str(SONOS_SCRIPT), action, "--target", target],
        capture_output=True,
        text=True
    )

    return {
        "exit_code": result.returncode,
        "output": result.stdout,
        "error": result.stderr
    }
