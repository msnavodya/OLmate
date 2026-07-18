import os
import sys
import traceback
from pathlib import Path

import uvicorn
from app.server import parse_port, select_available_port


if __name__ == "__main__":
    log_path = Path(__file__).with_name("run_dev.log")
    try:
        host = os.getenv("HOST", "127.0.0.1")
        requested_value = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PORT")
        requested_port = parse_port(requested_value)
        port = requested_port

        if requested_value is None:
            port = select_available_port(host, requested_port)

        message = f"Starting OL Mate API on http://{host}:{port}\n"
        if port != requested_port:
            message = (
                f"Port {requested_port} is already in use.\n"
                f"Starting OL Mate API on http://{host}:{port}\n"
            )

        print(message.strip())
        log_path.write_text(message, encoding="utf-8")
        uvicorn.run("main:app", host=host, port=port, log_level="info")
    except Exception:
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        raise
