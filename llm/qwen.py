from tabnanny import verbose

from llama_cpp import Llama


class Qwen:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            m_ctx=4096,  # what is this
            verbose=False,
        )

    def generate(self, prompt: str) -> str:
        response = self.llm(prompt, max_tokens=256, temperature=0)
        return response["choices"][0]["text"]
