# codex-utils

Lightweight Python helpers for working with an OpenAI-compatible Codex relay.

This package uses only the Python standard library and is suitable for Termux, Linux servers, and simple automation scripts.

## Features

- Chat Completions, non-stream
- Chat Completions, SSE stream
- Responses API, non-stream
- Responses API, SSE stream
- Local chat-session helper with history management
- No external dependencies

## Installation

### Local usage

Install directly from the folder:

```bash
pip install .
```

### Direct import without install

```bash
PYTHONPATH=. python3 your_script.py
```

## Environment variables

- `CODEX_BASE_URL` default: `https://codex.indrayuda.my.id/v1`
- `CODEX_API_KEY` default: `relay-internal-token`
- `CODEX_MODEL` default: `gpt-5.4`
- `CODEX_USER_AGENT` default: `Mozilla/5.0`
- `CODEX_TIMEOUT` default: `180`

## Quick start

### Stateless request

```python
from codex_utils import CodexClient

client = CodexClient()
reply = client.ask("Balas satu kata saja: halo")
print(reply)
```

### Streaming request

```python
from codex_utils import CodexClient

client = CodexClient()
client.ask_stream("Jelaskan Docker singkat", print_stream=True)
```

### Stateful local session

```python
from codex_utils import CodexChatSession

session = CodexChatSession(system_prompt="Jawab singkat dan teknis")
session.ask_stream("Apa itu Docker?", print_stream=True)
session.ask_stream("Bedanya dengan VM apa?", print_stream=True)
```

### Responses API

```python
from codex_utils import CodexClient

client = CodexClient()
text = client.responses_text("Balas satu kata saja: halo")
print(text)
```

## Core API

### `CodexClient`

Methods:

- `models()`
- `chat(messages, ...)`
- `chat_text(messages, ...)`
- `chat_stream(messages, ...)`
- `chat_stream_text(messages, ...)`
- `ask(prompt, ...)`
- `ask_stream(prompt, ...)`
- `responses(input_value, ...)`
- `responses_text(input_value, ...)`
- `responses_stream(input_value, ...)`
- `responses_stream_text(input_value, ...)`

### `CodexChatSession`

Methods:

- `ask(prompt, ...)`
- `ask_stream(prompt, ...)`
- `reset()`

## Error handling

HTTP failures raise `CodexAPIError`.

```python
from codex_utils import CodexClient, CodexAPIError

client = CodexClient()

try:
    print(client.ask("Halo"))
except CodexAPIError as exc:
    print(exc.status)
    print(exc.body)
```

## Example script

A runnable example is provided in `examples/quickstart.py`.
