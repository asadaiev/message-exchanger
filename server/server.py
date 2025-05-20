import http.server
import json
import argparse
from urllib.parse import urlparse, parse_qs

MAX_QUEUES = 100
MAX_MESSAGES_PER_QUEUE = 100
MAX_ALIAS = 10000

queues = {}

class MessageHandler(http.server.BaseHTTPRequestHandler):
    def _parse_alias(self, alias_str):
        if not alias_str.isdigit():
            return None
        alias = int(alias_str)
        if 0 <= alias <= MAX_ALIAS:
            return alias
        return None

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        try:
            data = json.loads(self.rfile.read(content_length))
            message = data.get("message", "").strip()
            alias_str = str(data.get("queue", "0"))
            alias = self._parse_alias(alias_str)
            if not message or alias is None:
                self.send_response(400)
                self.end_headers()
                return
        except:
            self.send_response(400)
            self.end_headers()
            return

        if alias not in queues:
            if len(queues) >= MAX_QUEUES:
                self.send_response(403)
                self.end_headers()
                return
            queues[alias] = []

        if len(queues[alias]) >= MAX_MESSAGES_PER_QUEUE:
            self.send_response(403)
            self.end_headers()
            return

        queues[alias].append(message)
        self.send_response(200)
        self.end_headers()


    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        alias_str = query.get("queue", ["0"])[0]
        alias = self._parse_alias(alias_str)
        if alias is None:
            self.send_response(400)
            self.end_headers()
            return

        if alias in queues and queues[alias]:
            message = queues[alias].pop(0)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(message.encode())
        else:
            self.send_response(204)
            self.end_headers()

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/clear_all":
            queues.clear()
            self.send_response(200)
            self.end_headers()
            return

        queue = query.get("queue", ["0"])[0]
        if not queue.isdigit() or not (0 <= int(queue) <= 10000):
            self.send_response(400)
            self.end_headers()
            return

        if queue in queues:
            queues[queue] = []
            self.send_response(200)
        else:
            self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return

def main():
    parser = argparse.ArgumentParser(description="Start message queue server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on")
    args = parser.parse_args()

    server = http.server.HTTPServer(('localhost', args.port), MessageHandler)
    print(f"Server running on port {args.port}...")
    server.serve_forever()

if __name__ == "__main__":
    main()
