UV = uv run
PYTHON = python3
PROGRAM = main.py

MODEL_DIR = models
MODEL_NAME = qwen3-0.6b-q4_k_m.gguf
MODEL_FILE = $(MODEL_DIR)/$(MODEL_NAME)
MODEL_URL = https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf

.PHONY: all run download-model model clean-model help

all: run

model download-model: $(MODEL_FILE)

$(MODEL_FILE):
	@echo "Creating $(MODEL_DIR) directory..."
	@mkdir -p $(MODEL_DIR)
	@echo "Downloading/Resuming Qwen GGUF model from Hugging Face to $(MODEL_FILE)..."
	curl -C - -L --progress-bar -o $(MODEL_FILE) "$(MODEL_URL)"
	@echo "Model downloaded successfully to $(MODEL_FILE)"

run: $(MODEL_FILE)
	$(UV) $(PYTHON) $(PROGRAM)

clean-model:
	rm -f $(MODEL_FILE)

force-download: clean-model download-model

help:
	@echo "AgentOS Makefile Commands:"
	@echo "  make / make run       - Download model (if missing) and run main.py"
	@echo "  make download-model   - Download the Qwen GGUF model to models/"
	@echo "  make force-download   - Delete partial/corrupted model and redownload fresh"
	@echo "  make clean-model      - Delete the downloaded GGUF model file"
