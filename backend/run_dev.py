import os
import sys
import traceback
from pathlib import Path

import uvicorn


if __name__ == "__main__":
    log_path = Path(__file__).with_name("run_dev.log")
    try:
        port = int(sys.argv[1] if len(sys.argv) > 1 else os.getenv("PORT", "8000"))
        log_path.write_text(f"Starting OL Mate API on port {port}\n", encoding="utf-8")
        uvicorn.run("main:app", host="127.0.0.1", port=port, log_level="info")
    except Exception:
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        raise
