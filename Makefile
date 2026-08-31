UV = uv run
PYTHON = python3
PROGRAM = main.py

MODEL_DIR = models
MODEL_NAME = qwen3-0.6b-q4_k_m.gguf
MODEL_FILE = $(MODEL_DIR)/$(MODEL_NAME)
MODEL_URL = https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf

.PHONY: all run download-model model clean-model force-download clean clean-pycache lint mypy flake8 check help

all: run

# Download the Qwen GGUF model from Hugging Face
model download-model: $(MODEL_FILE)

$(MODEL_FILE):
	@echo "Creating $(MODEL_DIR) directory..."
	@mkdir -p $(MODEL_DIR)
	@echo "Downloading/Resuming Qwen GGUF model from Hugging Face to $(MODEL_FILE)..."
	curl -C - -L --progress-bar -o $(MODEL_FILE) "$(MODEL_URL)"
	@echo "Model downloaded successfully to $(MODEL_FILE)"

# Run the interactive REPL
run: $(MODEL_FILE)
	$(UV) $(PYTHON) $(PROGRAM)

# Code Quality & Linting
flake8:
	$(UV) flake8 --max-line-length=100 --exclude .venv,__pycache__,build,dist,models .

mypy:
	$(UV) mypy --exclude .venv agent llm tools main.py

lint: flake8

check: flake8 mypy

clean-pycache clean:
	@echo "Removing __pycache__, .mypy_cache, and byte-compiled files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete
	@echo "Clean completed."

clean-model:
	rm -f $(MODEL_FILE)

force-download: clean-model download-model

help:
	@echo "AgentOS Makefile Commands:"
	@echo "  make / make run       - Run the interactive AgentOS REPL"
	@echo "  make download-model   - Download the Qwen GGUF model to models/"
	@echo "  make force-download   - Delete partial/corrupted model and redownload fresh"
	@echo "  make clean-pycache    - Delete all __pycache__, .mypy_cache, and .pyc files"
	@echo "  make flake8 / lint    - Run flake8 linter across codebase"
	@echo "  make mypy             - Run mypy static type checks"
	@echo "  make check            - Run both flake8 and mypy checks"
	@echo "  make clean-model      - Delete the downloaded GGUF model file"
