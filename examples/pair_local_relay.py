from codex_utils import CodexClient


def main() -> None:
    client = CodexClient()
    print(client.ask("Balas satu kata saja: halo"))


if __name__ == "__main__":
    main()
