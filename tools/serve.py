#!/usr/bin/env python3
"""Development server supporting root and /university/ deployment checks."""
import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '3000')))
parser.add_argument('--strictPort', action='store_true')
args = parser.parse_args()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def translate_path(self, path):
        if path.startswith('/university/'):
            path = path[len('/university'):]
        return super().translate_path(path)

    def do_GET(self):
        if urlsplit(self.path).path == '/university':
            self.send_response(301)
            self.send_header('Location', '/university/')
            self.end_headers()
        else:
            super().do_GET()

print(f'Serving {ROOT} at http://{args.host}:{args.port}/', flush=True)
ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
