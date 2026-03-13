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
    model="anthropic:claude-opus-4-6",
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

    # DEBUG: dump the raw result structure so we can see what's happening
    print("\n--- DEBUG: result keys ---")
    print(type(result), list(result.keys()) if isinstance(result, dict) else dir(result))

    result_msgs = result.get("messages", []) if isinstance(result, dict) else []
    print(f"\n--- DEBUG: {len(result_msgs)} messages ---")
    for i, msg in enumerate(result_msgs):
        msg_type = getattr(msg, "type", type(msg).__name__)
        content = getattr(msg, "content", None)
        content_type = type(content).__name__
        content_preview = str(content)[:200] if content else "(empty)"
        print(f"  [{i}] type={msg_type} content_type={content_type}: {content_preview}")

    # Display messages
    found_text = False
    for msg in result_msgs:
        if not hasattr(msg, "type"):
            continue
        if msg.type == "ai" and msg.content:
            if isinstance(msg.content, str):
                print(f"\n[ai]: {msg.content}")
                found_text = True
            elif isinstance(msg.content, list):
                for block in msg.content:
                    btype = block.get("type") if isinstance(block, dict) else getattr(block, "type", None)
                    if btype == "text":
                        text = block.get("text") if isinstance(block, dict) else block.text
                        print(f"\n[ai]: {text}")
                        found_text = True
                    elif btype == "tool_use":
                        name = block.get("name") if isinstance(block, dict) else getattr(block, "name", "?")
                        print(f"[tool]: called {name}")
        elif msg.type == "tool" and msg.content:
            content = str(msg.content)
            if len(content) > 300:
                content = content[:300] + "..."
            print(f"[result]: {content}")
        sys.stdout.flush()

    if not found_text:
        print("\n[ai]: (no text response — agent only performed actions)")

    # Keep full conversation history
    messages = result_msgs
