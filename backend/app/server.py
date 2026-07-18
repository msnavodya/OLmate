import socket


def parse_port(value: str | None, default: int = 8000) -> int:
    """Parse and validate a TCP port number."""
    if value is None or value == "":
        return default

    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid PORT value: {value!r}") from exc

    if not 1 <= port <= 65535:
        raise ValueError(f"PORT must be between 1 and 65535, got {port}")

    return port


def select_available_port(host: str, preferred_port: int, max_attempts: int = 20) -> int:
    """Return preferred_port when available, otherwise the next free port."""
    for port in range(preferred_port, preferred_port + max_attempts + 1):
        if _can_bind(host, port):
            return port

    raise OSError(
        f"No free port found from {preferred_port} to {preferred_port + max_attempts}"
    )


def _can_bind(host: str, port: int) -> bool:
    check_host = "" if host in {"0.0.0.0", "::"} else host
    family = socket.AF_INET6 if ":" in host and host != "0.0.0.0" else socket.AF_INET

    with socket.socket(family, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((check_host, port))
        except OSError:
            return False

    return True
