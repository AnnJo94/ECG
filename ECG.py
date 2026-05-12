import http.server
import os
import socketserver
import webbrowser
from pathlib import Path


PORT = 8000


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class ECGRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    root = Path(__file__).resolve().parent
    handler = lambda *args, **kwargs: ECGRequestHandler(*args, directory=str(root), **kwargs)

    server = None
    for port in range(PORT, PORT + 10):
        try:
            server = ReusableTCPServer(("", port), handler)
            break
        except OSError:
            continue

    if server is None:
        raise RuntimeError("No available local port found for the ECG dashboard.")

    with server:
        url = f"http://localhost:{server.server_address[1]}/web/index.html"
        print(f"ECG web dashboard running at {url}")
        if os.environ.get("ECG_NO_BROWSER") != "1":
            webbrowser.open(url)
        server.serve_forever()


if __name__ == "__main__":
    main()
