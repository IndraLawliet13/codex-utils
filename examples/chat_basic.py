from codex_utils import CodexClient

client = CodexClient()
reply = client.ask("Balas satu kata saja: halo")
print(reply)
