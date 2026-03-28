#!/usr/bin/env python3
# Qwen3.5-9B — Continuous interactive generation (MLX, Apple Silicon)
# Install: pip install mlx-lm

import signal
import sys
from mlx_lm import load, stream_generate

MODEL_NAME = "mlx-community/Qwen3.5-9B-8bit"
MAX_NEW_TOKENS = 1024

# --- Graceful shutdown: requires 2x Ctrl+C to exit ---
_interrupt_count = 0

def handle_interrupt(sig, frame):
    global _interrupt_count
    _interrupt_count += 1
    if _interrupt_count == 1:
        print("\n[Press Ctrl+C again to exit, or keep chatting]\n", flush=True)
    else:
        print("\nExiting.\n")
        sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

# --- Load model via MLX (uses Apple Silicon GPU natively) ---
print(f"\nLoading {MODEL_NAME} ...\n")
model, tokenizer = load(MODEL_NAME)
print("\nModel ready. Type a prompt and press Enter. Empty input is ignored.\n")
print("=" * 60)

# --- Continuous loop ---
while True:
    _interrupt_count = 0  # reset after each response

    try:
        user_input = input("\nYou: ").strip()
    except EOFError:
        break

    if not user_input:
        continue

    messages = [{"role": "user", "content": user_input}]
    formatted = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )

    print("\nAssistant: ", end="", flush=True)

    for token in stream_generate(
        model,
        tokenizer,
        prompt=formatted,
        max_tokens=MAX_NEW_TOKENS,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.1,
    ):
        print(token.text, end="", flush=True)

    print("\n" + "-" * 60)
