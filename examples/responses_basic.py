from codex_utils import CodexClient

client = CodexClient()
text = client.responses_text("Balas satu kata saja: halo")
print(text)
