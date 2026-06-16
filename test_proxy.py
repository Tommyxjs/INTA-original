#!/usr/bin/env python3
from openai import OpenAI

client = OpenAI(
    api_key="sk-vSPzUZZ4Germ1VKU7kaM8nrF0aB7S8WGnKvFOpWiGTatz4vi",
    base_url="https://www.yunqiaoai.top/v1",
)

try:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Ping test."},
        ],
        stream=False,
    )
    print("Success:", resp.choices[0].message.content)
except Exception as exc:
    print("Call failed:", repr(exc))