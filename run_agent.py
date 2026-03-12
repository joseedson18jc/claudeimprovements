from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a helpful coding assistant.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello! What can you help me with?"}]}
)

for msg in result["messages"]:
    print(f"[{msg.type}]: {msg.content}")
