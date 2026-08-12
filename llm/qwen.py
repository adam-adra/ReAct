from tabnanny import verbose

from llama_cpp import Llama


class Qwen:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            m_ctx=4096,  # what is this
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
            max_tokens=256,
        )
        return response["choices"][0]["message"]["content"]
