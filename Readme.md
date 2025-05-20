# 📨 Message Exchanger Exercise

Small Message Exchanger as an interview exercise
- `server.py` — receiving and saving messages in queue
- `client.py` — post and get messages 

---

## ⚙️ Requirements

- Python 3.10+
- (Optional) Docker + Docker Compose
- `pytest` (for test execution)

---

## 🚀 Local execution
### 1. Without Docker

Optional as tests checking if server is up and if not - start the server.
```bash
python server.py --port 8082
```

### 2. Test Execution
```
pip install pytest
pytest -s -v tests/test_client_tests.py
```

## 🐳 Запуск через Docker
### 1. Build images
```bash
docker compose build
```

### 2. Server execution

```bash
docker compose up -d server
```
### 3. POST
```bash
docker compose run --rm client POST --message "hello from Docker" --queue 2
```

### 4. GET
```bash
docker compose run --rm client GET --queue 2
```

## 🧪 Запуск тестів при роботі сервера в Docker
Run the created script
```bash
run_tests.sh
```

## 😭Manual validation from command line

### POST

```
python client/client.py POST --host "localhost" --port "8082" --message "First Message" --queue 0

OR

python client/client.py POST --message "First Message" --queue 0

```
### GET

```

python client/client.py GET --host "localhost" --port "8082" --queue 0

OR 

python client/client.py GET  --queue 0

```

## 🐳 Help

```Bash
python client/client.py --help

python server/server.py --help
```
