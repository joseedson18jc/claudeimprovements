from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends.local_shell import LocalShellBackend

home_dir = str(Path.home())

backend = LocalShellBackend(root_dir="/", virtual_mode=False)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=(
        "You are a helpful coding assistant. "
        f"The user's home directory is {home_dir}. "
        "You have full access to the entire filesystem. "
        "When searching for files, use absolute paths."
    ),
    backend=backend,
)

messages = []

print("Deep Agent Chat (type 'exit' or 'quit' to stop)")
print("-" * 50)

while True:
    try:
        user_input = input("\n[you]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        break

    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        print("Goodbye!")
        break

    messages.append({"role": "user", "content": user_input})

    result = agent.invoke({"messages": messages})

    # Get the last AI message from the result
    for msg in result["messages"]:
        if msg.type == "ai" and msg.content:
            print(f"\n[ai]: {msg.content}")

    # Keep full conversation history for context
    messages = result["messages"]
