import argparse
import http.client
import json
import sys

def validate_alias(alias_str):
    if not alias_str.isdigit():
        raise argparse.ArgumentTypeError("Queue alias must be a number from 0 to 10000.")
    alias = int(alias_str)
    if 0 <= alias <= 10000:
        return alias_str
    raise argparse.ArgumentTypeError("Queue alias must be in range 0 to 10000.")

def post_message(host, port, message, queue="0"):
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"message": message, "queue": queue})
    conn.request("POST", "/", body, headers)
    return conn.getresponse().status

def get_message(host, port, queue="0"):
    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", f"/?queue={queue}")
    response = conn.getresponse()
    return response.status, response.read().decode()

def main():
    parser = argparse.ArgumentParser(description="Client for sending/receiving messages to/from server.")
    parser.add_argument("method", choices=["POST", "GET"], help="Request method")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8082, help="Server port")
    parser.add_argument("--message", help="Message to send (for POST only)")
    parser.add_argument("--queue", type=validate_alias, default="0", help="Queue alias (0-10000)")

    args = parser.parse_args()

    if args.method == "POST":
        status = post_message(args.host, args.port, args.message, args.queue)
    else:
        status = get_message(args.host, args.port, args.queue)

    print("Status: ", status)
    sys.exit(status)

if __name__ == "__main__":
    main()
