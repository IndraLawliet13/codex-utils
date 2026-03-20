from codex_utils import CodexClient

client = CodexClient()
client.responses_stream_text("Jelaskan SSE singkat", print_stream=True)
