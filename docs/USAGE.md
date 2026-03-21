# Usage Guide

This guide shows the most common usage patterns for `codex-utils`.

## 1. Simple one-shot request

```python
from codex_utils import CodexClient

client = CodexClient()
reply = client.ask("Balas satu kata saja: halo")
print(reply)
```

## 2. Streaming output

```python
from codex_utils import CodexClient

client = CodexClient()
client.ask_stream("Jelaskan Docker singkat", print_stream=True)
```

## 3. Stateful local chat session

```python
from codex_utils import CodexChatSession

session = CodexChatSession(system_prompt="Jawab singkat dan teknis")
session.ask_stream("Apa itu Docker?", print_stream=True)
session.ask_stream("Bedanya dengan VM apa?", print_stream=True)
```

Use `reset()` when you want to clear local history.

```python
session.reset()
```

## 4. Raw chat-completions messages

```python
from codex_utils import CodexClient

client = CodexClient()
messages = [
    {"role": "system", "content": "Jawab singkat."},
    {"role": "user", "content": "Apa itu reverse proxy?"},
]

payload = client.chat(messages)
print(payload)
print(client.chat_text(messages))
```

## 5. Responses API

```python
from codex_utils import CodexClient

client = CodexClient()
text = client.responses_text("Balas satu kata saja: halo")
print(text)
```

Streaming version:

```python
from codex_utils import CodexClient

client = CodexClient()
client.responses_stream_text("Jelaskan SSE singkat", print_stream=True)
```

## 6. Custom configuration

```python
from codex_utils import CodexClient

client = CodexClient(
    base_url="http://127.0.0.1:8787/v1",
    api_key="relay-dev-token",
    model="gpt-5.4",
    timeout=240,
)

print(client.ask("Halo"))
```

## 7. Session key forwarding

If your upstream supports sticky session behavior, pass `session_key`.

```python
from codex_utils import CodexClient

client = CodexClient()
reply = client.ask(
    "Halo",
    session_key="my-app-session-123",
)
print(reply)
```

## 8. Error handling

```python
from codex_utils import CodexClient, CodexAPIError

client = CodexClient()

try:
    print(client.ask("Halo"))
except CodexAPIError as exc:
    print("status:", exc.status)
    print("body:", exc.body)
```

## 9. Listing available models

```python
from codex_utils import CodexClient

client = CodexClient()
print(client.models())
```

## 10. Environment variables

Supported environment variables:

- `CODEX_BASE_URL`
- `CODEX_API_KEY`
- `CODEX_MODEL`
- `CODEX_USER_AGENT`
- `CODEX_TIMEOUT`

Example:

```bash
export CODEX_BASE_URL="http://127.0.0.1:8787/v1"
export CODEX_API_KEY="relay-dev-token"
python3 your_script.py
```

## 11. Pairing with codex-slot-relay

Recommended backend relay repo:
- `https://github.com/IndraLawliet13/codex-slot-relay`

See also:
- `docs/CODEX_SLOT_RELAY.md`
