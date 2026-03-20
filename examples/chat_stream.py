from codex_utils import CodexClient

client = CodexClient()
client.ask_stream("Jelaskan Docker singkat", print_stream=True)
