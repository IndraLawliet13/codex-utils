from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Iterator, List, Optional

__version__ = "0.1.0"

DEFAULT_BASE_URL = os.getenv("CODEX_BASE_URL", "https://codex.indrayuda.my.id/v1").rstrip("/")
DEFAULT_API_KEY = os.getenv("CODEX_API_KEY", "relay-internal-token")
DEFAULT_MODEL = os.getenv("CODEX_MODEL", "gpt-5.4")
DEFAULT_USER_AGENT = os.getenv("CODEX_USER_AGENT", "Mozilla/5.0")
DEFAULT_TIMEOUT = int(os.getenv("CODEX_TIMEOUT", "180"))


class CodexAPIError(RuntimeError):
    def __init__(self, status: int, body: str, headers: Optional[Dict[str, Any]] = None):
        self.status = status
        self.body = body
        self.headers = headers or {}
        self.payload = _try_json_loads(body)
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        if isinstance(self.payload, dict):
            err = self.payload.get("error")
            if isinstance(err, dict):
                msg = err.get("message")
                if msg:
                    return f"HTTP {self.status}: {msg}"
        compact = self.body.strip().replace("\n", " ")
        if len(compact) > 220:
            compact = compact[:220] + "..."
        return f"HTTP {self.status}: {compact or 'Unknown error'}"


class CodexClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = DEFAULT_API_KEY,
        model: str = DEFAULT_MODEL,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.user_agent = user_agent
        self.timeout = int(timeout)

    def models(self) -> Dict[str, Any]:
        return self._json_request("GET", "/models")

    def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
        }
        if user:
            payload["user"] = user
        if extra:
            payload.update(extra)
        return self._json_request("POST", "/chat/completions", payload=payload, session_key=session_key)

    def chat_text(self, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        return extract_chat_text(self.chat(messages, **kwargs))

    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "model": model or self.model,
            "stream": True,
            "messages": messages,
        }
        if user:
            payload["user"] = user
        if extra:
            payload.update(extra)
        yield from self._stream_request("/chat/completions", payload=payload, session_key=session_key)

    def chat_stream_text(self, messages: List[Dict[str, Any]], *, print_stream: bool = False, out=None, **kwargs: Any) -> str:
        pieces: List[str] = []
        output = out or sys.stdout
        for event in self.chat_stream(messages, **kwargs):
            if event.get("done"):
                break
            payload = event.get("json") or {}
            choices = payload.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            piece = delta.get("content")
            if not piece:
                continue
            pieces.append(piece)
            if print_stream:
                print(piece, end="", flush=True, file=output)
        if print_stream:
            print(file=output)
        return "".join(pieces)

    def ask(
        self,
        prompt: str,
        *,
        history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: str = "",
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        messages = build_messages(prompt, history=history, system_prompt=system_prompt)
        return self.chat_text(messages, model=model, user=user, session_key=session_key, extra=extra)

    def ask_stream(
        self,
        prompt: str,
        *,
        history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: str = "",
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        print_stream: bool = False,
        out=None,
    ) -> str:
        messages = build_messages(prompt, history=history, system_prompt=system_prompt)
        return self.chat_stream_text(
            messages,
            model=model,
            user=user,
            session_key=session_key,
            extra=extra,
            print_stream=print_stream,
            out=out,
        )

    def responses(
        self,
        input_value: Any,
        *,
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
        instructions: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model or self.model,
            "input": input_value,
        }
        if instructions:
            payload["instructions"] = instructions
        if user:
            payload["user"] = user
        if extra:
            payload.update(extra)
        return self._json_request("POST", "/responses", payload=payload, session_key=session_key)

    def responses_text(self, input_value: Any, **kwargs: Any) -> str:
        return extract_response_text(self.responses(input_value, **kwargs))

    def responses_stream(
        self,
        input_value: Any,
        *,
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
        instructions: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "model": model or self.model,
            "stream": True,
            "input": input_value,
        }
        if instructions:
            payload["instructions"] = instructions
        if user:
            payload["user"] = user
        if extra:
            payload.update(extra)
        yield from self._stream_request("/responses", payload=payload, session_key=session_key)

    def responses_stream_text(self, input_value: Any, *, print_stream: bool = False, out=None, **kwargs: Any) -> str:
        pieces: List[str] = []
        output = out or sys.stdout
        for event in self.responses_stream(input_value, **kwargs):
            if event.get("done"):
                break
            payload = event.get("json") or {}
            event_name = event.get("event") or payload.get("type")
            if event_name != "response.output_text.delta":
                continue
            piece = payload.get("delta")
            if not piece:
                continue
            pieces.append(piece)
            if print_stream:
                print(piece, end="", flush=True, file=output)
        if print_stream:
            print(file=output)
        return "".join(pieces)

    def _json_request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        session_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        req = self._build_request(method, path, payload=payload, session_key=session_key, stream=False)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                data = _try_json_loads(body)
                if not isinstance(data, dict):
                    raise RuntimeError(f"Expected JSON object, got: {body[:300]}")
                return data
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise CodexAPIError(exc.code, body, headers=dict(exc.headers)) from None

    def _stream_request(
        self,
        path: str,
        payload: Dict[str, Any],
        session_key: Optional[str] = None,
    ) -> Iterator[Dict[str, Any]]:
        req = self._build_request("POST", path, payload=payload, session_key=session_key, stream=True)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                yield from _iter_sse_json_events(resp)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise CodexAPIError(exc.code, body, headers=dict(exc.headers)) from None

    def _build_request(
        self,
        method: str,
        path: str,
        *,
        payload: Optional[Dict[str, Any]] = None,
        session_key: Optional[str] = None,
        stream: bool = False,
    ) -> urllib.request.Request:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self.user_agent,
            "Accept": "text/event-stream" if stream else "application/json",
        }
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")
        if session_key:
            headers["x-openclaw-session-key"] = session_key
        return urllib.request.Request(
            self.base_url + path,
            data=data,
            headers=headers,
            method=method,
        )


class CodexChatSession:
    def __init__(
        self,
        client: Optional[CodexClient] = None,
        *,
        system_prompt: str = "",
        model: Optional[str] = None,
        user: Optional[str] = None,
        session_key: Optional[str] = None,
    ):
        self.client = client or CodexClient()
        self.system_prompt = system_prompt
        self.model = model
        self.user = user
        self.session_key = session_key
        self.history: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self.history = []

    def messages(self, prompt: str) -> List[Dict[str, Any]]:
        return build_messages(prompt, history=self.history, system_prompt=self.system_prompt)

    def ask(self, prompt: str, *, extra: Optional[Dict[str, Any]] = None) -> str:
        reply = self.client.ask(
            prompt,
            history=self.history,
            system_prompt=self.system_prompt,
            model=self.model,
            user=self.user,
            session_key=self.session_key,
            extra=extra,
        )
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def ask_stream(self, prompt: str, *, extra: Optional[Dict[str, Any]] = None, print_stream: bool = False, out=None) -> str:
        reply = self.client.ask_stream(
            prompt,
            history=self.history,
            system_prompt=self.system_prompt,
            model=self.model,
            user=self.user,
            session_key=self.session_key,
            extra=extra,
            print_stream=print_stream,
            out=out,
        )
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": reply})
        return reply


def build_messages(
    prompt: str,
    *,
    history: Optional[List[Dict[str, Any]]] = None,
    system_prompt: str = "",
    developer_prompt: str = "",
) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    if developer_prompt.strip():
        messages.append({"role": "developer", "content": developer_prompt.strip()})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    return messages


def extract_chat_text(payload: Dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)


def extract_response_text(payload: Dict[str, Any]) -> str:
    output = payload.get("output") or []
    parts: List[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message":
            continue
        for content in item.get("content") or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "".join(parts)


def _iter_sse_frames(resp) -> Iterator[Dict[str, Optional[str]]]:
    event_name: Optional[str] = None
    data_lines: List[str] = []
    for raw_line in resp:
        line = raw_line.decode("utf-8", errors="replace").rstrip("\n")
        if line.endswith("\r"):
            line = line[:-1]
        if not line:
            if data_lines or event_name:
                yield {"event": event_name, "data": "\n".join(data_lines)}
                event_name = None
                data_lines = []
            continue
        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event_name = line.split(":", 1)[1].lstrip()
            continue
        if line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].lstrip())
            continue
    if data_lines or event_name:
        yield {"event": event_name, "data": "\n".join(data_lines)}


def _iter_sse_json_events(resp) -> Iterator[Dict[str, Any]]:
    for frame in _iter_sse_frames(resp):
        raw_data = frame.get("data") or ""
        if raw_data == "[DONE]":
            yield {"event": frame.get("event"), "done": True, "raw": raw_data, "json": None}
            return
        parsed = _try_json_loads(raw_data)
        yield {
            "event": frame.get("event"),
            "done": False,
            "raw": raw_data,
            "json": parsed if isinstance(parsed, dict) else None,
        }


def _try_json_loads(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return None


__all__ = [
    "__version__",
    "CodexAPIError",
    "CodexClient",
    "CodexChatSession",
    "build_messages",
    "extract_chat_text",
    "extract_response_text",
]
