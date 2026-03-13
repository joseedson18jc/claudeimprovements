import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY is not set.")
    print("Set it via: export ANTHROPIC_API_KEY='your-key'")
    print("Or create a .env file with: ANTHROPIC_API_KEY=your-key")
    sys.exit(1)

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

    print()

    # Stream events in real-time so output isn't stuck
    all_new_msgs = []
    for event in agent.stream({"messages": messages}, stream_mode="updates"):
        for node_name, node_data in event.items():
            msgs = node_data.get("messages", [])
            for msg in msgs:
                all_new_msgs.append(msg)
                if msg.type == "ai" and msg.content:
                    if isinstance(msg.content, str):
                        print(f"[ai]: {msg.content}")
                    elif isinstance(msg.content, list):
                        for block in msg.content:
                            btype = block.get("type") if isinstance(block, dict) else getattr(block, "type", None)
                            if btype == "text":
                                text = block.get("text") if isinstance(block, dict) else block.text
                                print(f"[ai]: {text}")
                            elif btype == "tool_use":
                                name = block.get("name") if isinstance(block, dict) else getattr(block, "name", "?")
                                print(f"[tool]: calling {name}...")
                elif msg.type == "tool" and msg.content:
                    content = str(msg.content)
                    if len(content) > 300:
                        content = content[:300] + "..."
                    print(f"[result]: {content}")
                sys.stdout.flush()

    # Build conversation history from streamed messages
    messages = messages + all_new_msgs
