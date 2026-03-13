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

    print("\n[thinking...]")
    result = agent.invoke({"messages": messages})

    # Print all AI text responses and tool activity
    found_text = False
    for msg in result["messages"]:
        if msg.type == "ai" and msg.content:
            if isinstance(msg.content, str):
                print(f"\n[ai]: {msg.content}")
                found_text = True
            elif isinstance(msg.content, list):
                text_parts = []
                tool_names = []
                for block in msg.content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_parts.append(block["text"])
                        elif block.get("type") == "tool_use":
                            tool_names.append(block.get("name", "unknown"))
                    elif hasattr(block, "type"):
                        if block.type == "text":
                            text_parts.append(block.text)
                        elif block.type == "tool_use":
                            tool_names.append(getattr(block, "name", "unknown"))
                if tool_names:
                    print(f"\n[tool]: {', '.join(tool_names)}")
                if text_parts:
                    print(f"\n[ai]: {''.join(text_parts)}")
                    found_text = True
        elif msg.type == "tool" and msg.content:
            # Show truncated tool output
            content = str(msg.content)
            if len(content) > 500:
                content = content[:500] + "..."
            print(f"\n[result]: {content}")

    if not found_text:
        print("\n[ai]: (no text response — agent may have only performed actions)")

    # Keep full conversation history for context
    messages = result["messages"]
