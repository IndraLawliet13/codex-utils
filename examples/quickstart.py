from codex_utils import CodexChatSession, CodexClient

client = CodexClient()
print(client.ask("Balas satu kata saja: halo"))
client.ask_stream("Jelaskan Docker singkat", print_stream=True)

session = CodexChatSession(system_prompt="Jawab singkat dan teknis")
session.ask_stream("Apa itu Docker?", print_stream=True)
session.ask_stream("Bedanya dengan VM apa?", print_stream=True)
