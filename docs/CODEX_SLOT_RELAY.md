# Using codex-utils with codex-slot-relay

`codex-utils` is designed to pair directly with:
- `https://github.com/IndraLawliet13/codex-slot-relay`

## Local defaults

The package defaults assume a local relay is running at:

- `CODEX_BASE_URL=http://127.0.0.1:8787/v1`
- `CODEX_API_KEY=relay-dev-token`

So the easiest workflow is:

1. start `codex-slot-relay`
2. install `codex-utils`
3. call `CodexClient()` with no extra config

## Example

```python
from codex_utils import CodexClient

client = CodexClient()
print(client.ask("Balas satu kata saja: halo"))
```

A runnable file is also included:

```bash
python3 examples/pair_local_relay.py
```

## If you want custom values

```bash
export CODEX_BASE_URL="http://127.0.0.1:8787/v1"
export CODEX_API_KEY="relay-dev-token"
```

Or override in code:

```python
from codex_utils import CodexClient

client = CodexClient(
    base_url="http://127.0.0.1:8787/v1",
    api_key="relay-dev-token",
)
```
