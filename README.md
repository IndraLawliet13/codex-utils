# codex-utils

[![Release](https://img.shields.io/github/v/release/IndraLawliet13/codex-utils?display_name=tag)](https://github.com/IndraLawliet13/codex-utils/releases)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/IndraLawliet13/codex-utils)](LICENSE)
[![API](https://img.shields.io/badge/api-openai--compatible-black)](https://github.com/IndraLawliet13/codex-utils)

Lightweight Python helpers for OpenAI-compatible Codex relay endpoints.

`codex-utils` is a small, dependency-free Python library for projects that want a clean interface to:

- `POST /v1/chat/completions`
- `POST /v1/responses`
- SSE streaming for both APIs
- local chat-session helpers with history management

It is designed to work well in lightweight environments such as Termux, VPS automation scripts, and simple backend services where adding third-party HTTP clients is unnecessary.

## Highlights

- No external dependencies
- Chat Completions support
- Responses API support
- SSE stream helpers
- Local conversation/session helper
- Works with plain Python standard library

## Installation

### Install from the repository folder

```bash
pip install .
```

### Quick install for local testing

```bash
git clone https://github.com/IndraLawliet13/codex-utils.git
cd codex-utils
pip install .
```

### Install directly from GitHub

```bash
pip install git+https://github.com/IndraLawliet13/codex-utils.git
```

### Install a tagged release

```bash
pip install git+https://github.com/IndraLawliet13/codex-utils.git@v0.1.0
```

### Import without installation

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

Main methods:

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

Session helper methods:

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

A runnable example is available at:

- `examples/quickstart.py`

## Changelog

See `CHANGELOG.md` for release history.

## License

MIT. See `LICENSE`.
