from typing import cast
from llama_cpp import Llama


class Qwen:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            verbose=False,
        )

    def generate(self, system_prompt: str, user_prompt: str, schema: dict) -> str:
        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object", "schema": schema},
            temperature=0.0,
            repeat_penalty=1.15,
            max_tokens=1024,
        )
        if isinstance(response, dict):
            content = response["choices"][0]["message"].get("content")
            return cast(str, content or "")
        return ""
