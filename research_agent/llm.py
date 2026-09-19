"""Thin wrapper around a small open-weight instruct model (Hugging Face transformers)."""

from __future__ import annotations

import threading

DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


class LLMEngine:
    """Loads one small instruct model and exposes a simple chat-completion call.

    The model is loaded lazily (on first use) and cached on the instance, since
    loading weights is the expensive part and callers may build several
    ResearchAgent objects without ever calling .research().
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str | None = None):
        self.model_name = model_name
        self.device = device
        self._pipeline = None
        self._lock = threading.Lock()

    def _load(self):
        if self._pipeline is not None:
            return
        with self._lock:
            if self._pipeline is not None:
                return
            import torch
            from transformers import pipeline

            device = self.device
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"

            self._pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                dtype="auto",
                device_map=device if device == "cuda" else None,
            )

    def chat(self, system_prompt: str, user_prompt: str, max_new_tokens: int = 200) -> str:
        """Run one chat-style completion and return the assistant's reply text."""
        self._load()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        prompt = self._pipeline.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        outputs = self._pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_full_text=False,
        )
        return outputs[0]["generated_text"].strip()
