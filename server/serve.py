#!/usr/bin/env python3
"""
Minimal, dependency-free HA-cluster node identity page.

Deploy this exact same file on every node. Each node only needs a
different NODE_NAME (env var or CLI arg) so you can eyeball which
box is actually answering behind the floating VIP.

Run:
    python3 server.py                       # defaults to "node 1"
    NODE_NAME="node 2" python3 server.py    # on the second box
    python3 server.py --node "node 2" --port 8000
"""

import argparse
import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------------------------------------------------------------------------
# Palette: each entry is (background, shape-color, accent-text-color)
# Picked so the dark shapes + light text always stay readable on top
# of the randomly chosen background.
# ---------------------------------------------------------------------------
PALETTE = [
    ("#c6d68a", "#33421a", "#eef3d6"),  # olive / moss
    ("#f4a6a6", "#5c1a1a", "#fdeaea"),  # coral / brick
    ("#a6c8f4", "#122a52", "#e8f1fd"),  # sky / navy
    ("#f7d774", "#5c4a12", "#fdf6e0"),  # gold / mustard
    ("#c9a6f4", "#341a5c", "#f1e8fd"),  # lilac / plum
    ("#a6f4d0", "#0f4a33", "#e6fdf3"),  # mint / forest
    ("#f4b6d4", "#5c1240", "#fde8f3"),  # pink / berry
    ("#f4c2a6", "#5c2a12", "#fdeee0"),  # peach / rust
    ("#b6f4a6", "#1f5c12", "#eefde6"),  # lime / pine
    ("#d0d0f4", "#1a1a5c", "#e9e9fd"),  # periwinkle / indigo
]

TAGLINES = [
    "the failover worked and someone is still watching.",
    "quorum achieved. traffic is flowing. all is well.",
    "if you can see this, the VIP found a home.",
    "elected, promoted, and serving like it means it.",
    "no split-brain here, just one node doing the job.",
    "heartbeat detected. this box is the chosen one.",
]


def render_page(node_name: str) -> str:
    bg, shape, text = random.choice(PALETTE)
    tagline = random.choice(TAGLINES)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{node_name} · live</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body {{
        height: 100%;
        background: {bg};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     Helvetica, Arial, sans-serif;
        transition: background 0.4s ease;
    }}

    .wrap {{
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 36px;
        padding: 40px 20px;
    }}

    /* ---- geometric mark, built entirely from clip-path shapes ---- */
    .mark {{
        display: grid;
        grid-template-columns: repeat(4, 64px);
        grid-template-rows: repeat(3, 64px);
        gap: 24px 26px;
        justify-content: center;
    }}

    .shape {{ background: {shape}; width: 64px; height: 64px; }}

    .flag        {{ clip-path: polygon(0 0, 100% 0, 0 100%); }}
    .flag-mirror {{ clip-path: polygon(100% 0, 100% 100%, 0 100%); }}
    .diamond     {{ clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }}
    .down        {{ clip-path: polygon(0 0, 100% 0, 50% 100%); }}
    .bowtie      {{ clip-path: polygon(0 0, 100% 50%, 0 100%, 50% 50%, 100% 0, 50% 50%, 100% 100%); }}
    .empty       {{ background: transparent; }}

    /* row 1 */
    .r1c1 {{ grid-row: 1; grid-column: 1; }}
    .r1c2 {{ grid-row: 1; grid-column: 2; }}
    .r1c3 {{ grid-row: 1; grid-column: 3; }}
    .r1c4 {{ grid-row: 1; grid-column: 4; }}
    /* row 2 (only two shapes, centred under row 1 / row 3) */
    .r2c2 {{ grid-row: 2; grid-column: 2; }}
    .r2c3 {{ grid-row: 2; grid-column: 3; }}
    /* row 3 mirrors row 1 */
    .r3c1 {{ grid-row: 3; grid-column: 1; }}
    .r3c2 {{ grid-row: 3; grid-column: 2; }}
    .r3c3 {{ grid-row: 3; grid-column: 3; }}
    .r3c4 {{ grid-row: 3; grid-column: 4; }}

    .tagline {{
        font-size: 19px;
        color: {shape};
        opacity: 0.85;
        text-align: center;
        max-width: 480px;
    }}

    .badge {{
        background: {shape};
        color: {text};
        font-size: 17px;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        padding: 16px 30px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
    }}

    .pulse {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: {text};
        box-shadow: 0 0 0 rgba(0,0,0,0);
        animation: pulse 1.6s infinite;
    }}

    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 {text}66; }}
        70%  {{ box-shadow: 0 0 0 10px {text}00; }}
        100% {{ box-shadow: 0 0 0 0 {text}00; }}
    }}

    .footnote {{
        font-size: 12px;
        color: {shape};
        opacity: 0.55;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}
</style>
</head>
<body>
    <div class="wrap">
        <div class="mark">
            <div class="shape flag r1c1"></div>
            <div class="shape diamond r1c2"></div>
            <div class="shape down r1c3"></div>
            <div class="shape flag-mirror r1c4"></div>

            <div class="shape diamond r2c2"></div>
            <div class="shape bowtie r2c3"></div>

            <div class="shape flag r3c1"></div>
            <div class="shape diamond r3c2"></div>
            <div class="shape down r3c3"></div>
            <div class="shape flag-mirror r3c4"></div>
        </div>

        <p class="tagline">{tagline}</p>

        <div class="badge">
            <span class="pulse"></span>
            <span>Serving from {node_name}</span>
        </div>
    </div>
</body>
</html>
"""


def make_handler(node_name: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = render_page(node_name).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        # keep the access log quiet-ish but still useful
        def log_message(self, fmt, *args):
            print(f"[{node_name}] {self.address_string()} - {fmt % args}")

    return Handler


def main():
    parser = argparse.ArgumentParser(description="HA cluster node identity page")
    parser.add_argument(
        "--node",
        default=os.environ.get("NODE_NAME", "node 1"),
        help="Label shown on the page (default: env NODE_NAME or 'node 1')",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8000)),
        help="Port to listen on (default: env PORT or 8000)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Address to bind to (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), make_handler(args.node))
    print(f"Serving '{args.node}' on http://{args.host}:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()

