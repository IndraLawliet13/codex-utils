# Changelog

## v0.2.0 - 2026-03-22

Sync release for local pairing with `codex-slot-relay`.

### Changed
- default `CODEX_BASE_URL` is now `http://127.0.0.1:8787/v1`
- default `CODEX_API_KEY` is now `relay-dev-token`
- README and usage docs now document the recommended pairing with `codex-slot-relay`

### Added
- `docs/CODEX_SLOT_RELAY.md`

## v0.1.0 - 2026-03-21

Initial public release.

### Added
- `CodexClient` for OpenAI-compatible chat and responses requests
- SSE streaming helpers for chat completions and responses APIs
- `CodexChatSession` for local history/session convenience
- dependency-free implementation using only Python standard library
- Termux/VPS-friendly examples and package metadata
