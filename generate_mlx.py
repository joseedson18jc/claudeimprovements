# MLX-LM Text Generation Script
# Requires: Apple Silicon Mac (M1/M2/M3/M4)
# Install: pip install --upgrade mlx-lm

import platform
import sys

if platform.system() != "Darwin" or platform.machine() != "arm64":
    print("Error: mlx-lm requires an Apple Silicon Mac (M-series chip).")
    print(f"Current platform: {platform.system()} {platform.machine()}")
    sys.exit(1)

from mlx_lm import load, generate

model, tokenizer = load("mlx-community/Qwen2.5-7B-Instruct-4bit")

prompt = "Write a story about Einstein"
messages = [{"role": "user", "content": prompt}]
prompt = tokenizer.apply_chat_template(
    messages, add_generation_prompt=True
)

text = generate(model, tokenizer, prompt=prompt, verbose=True)
