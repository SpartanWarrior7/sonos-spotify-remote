from fastapi import FastAPI, HTTPException
import subprocess
from fastapi.responses import FileResponse

app = FastAPI()

# SAFETY: only these programs are allowed
PROGRAMS = {
    "hello": "./scripts/hello.sh",
	"sonos_playpause_luke": "./scripts/sonos_playpause_luke.sh"
}

@app.get("/")
def home_page():
    return FileResponse("index.html")


@app.get("/run/{program}")
def run_program(program: str):
    if program not in PROGRAMS:
        raise HTTPException(status_code=404, detail="Program not allowed")

    result = subprocess.run(
        PROGRAMS[program],
        shell=True,
        capture_output=True,
        text=True
    )

    return {
        "exit_code": result.returncode,
        "output": result.stdout,
        "error": result.stderr
    }
