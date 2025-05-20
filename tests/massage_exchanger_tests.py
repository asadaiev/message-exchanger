import pytest
import subprocess
import time
import http.client
import json
import random

PORT = 8082
HOST = "localhost"

def is_server_running(host, port):
    try:
        conn = http.client.HTTPConnection(host, port, timeout=1)
        conn.request("GET", "/")
        resp = conn.getresponse()
        return resp.status in (200, 204, 400)
    except Exception:
        return False

@pytest.fixture(scope="session", autouse=True)
def start_server():
    if is_server_running(HOST, PORT):
        print(f"Server already running at {HOST}:{PORT}, skipping start.")
        yield
    else:
        print(f"Starting server at {HOST}:{PORT}...")
        proc = subprocess.Popen(["python", "server/server.py", "--port", str(PORT)])
        time.sleep(1)
        yield
        proc.terminate()
        proc.wait()

def clear_all_queues():
    conn = http.client.HTTPConnection("localhost", PORT)
    conn.request("DELETE", "/clear_all")
    resp = conn.getresponse()
    return resp.status

@pytest.fixture(autouse=True)
def clear_queues_before_each_test():
    clear_all_queues()
    yield
    clear_all_queues()

def send_post(message, queue="0"):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"message": message, "queue": queue})
    conn.request("POST", "/", body, headers)
    return conn.getresponse().status

def send_get(queue="0"):
    conn = http.client.HTTPConnection(HOST, PORT)
    conn.request("GET", f"/?queue={queue}")
    response = conn.getresponse()
    return response.status, response.read().decode()

def test_valid_post_and_get():
    assert send_post("Hello", "0") == 200
    status, message = send_get("0")
    assert status == 200
    assert message == "Hello"

def test_default_queue():
    assert send_post("default message") == 200
    status, message = send_get()
    assert status == 200
    assert message == "default message"

def test_empty_post_message():
    assert send_post("", "0") == 400

def test_invalid_queue_alias_post():
    assert send_post("test", "-1") == 400
    assert send_post("test", "10001") == 400
    assert send_post("test", "abc") == 400

def test_invalid_queue_alias_get():
    assert send_get("-5")[0] == 400
    assert send_get("10001")[0] == 400
    assert send_get("xyz")[0] == 400

def test_queue_limit():
    for i in range(100):
        assert send_post("fill", str(i)) == 200
    assert send_post("should fail", "100") == 403

def test_queue_limit_behavior():
    queue = 9985
    for i in range(100):
        response = send_post(f"message-{i}", str(queue))
        assert response == 200, f"Message {i} failed to send"

    response = send_post("overflow-message", queue)
    assert response == 403, "Overflow message was incorrectly accepted"

def test_empty_queue_get():
    status, message = send_get("8888")
    assert status == 204

def test_get_removes_message():
    queue = str(random.randint(2001, 3000))
    msg = "test-message"
    assert send_post(msg, queue) == 200
    status, message = send_get(queue)
    assert status == 200
    assert message == msg
    status, _ = send_get(queue)
    assert status == 204
