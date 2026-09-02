# AgentOS: A From-Scratch Modular Agent Runtime

AgentOS is a modular, local-first runtime and execution harness designed to operate autonomous AI agents using quantized local models (such as Qwen 2.5 / Qwen 3 0.5B-0.6B GGUF) via llama.cpp.

The project is built around a core architectural principle:

$$\text{Agent} = \text{Model} + \text{Harness}$$

The Large Language Model is not the agent. The model functions as the reasoning engine and decision policy, while the runtime harness provides state management, tool registries, grammar-constrained decoding, sandboxed execution, exception containment, and trajectory memory.

---

## 1. System Architecture

The runtime decomposes the autonomous execution loop into decoupled subsystems following the Sense-Decide-Act pattern.

```
                         +-------------------+
                         |     User Goal     |
                         +---------+---------+
                                   |
                                   v
+-------------------------------------------------------------------------+
|                              Agent Loop                                 |
|                                                                         |
|   1. Sense: Collect Observation from Environment                        |
|   2. Decide: Query Policy Adapter (DecisionMaker)                       |
|   3. Verify: Check if Action is Final or Tool                           |
|   4. Act: Execute Action in Environment Sandbox                         |
|   5. Record: Update Trajectory History                                  |
+-------------------+---------------------------------+-------------------+
                    |                                 ^
             Action |                                 | Observation
                    v                                 |
+------------------------------------+  +---------------------------------+
|        Environment Sandbox         |  |         Decision Policy         |
|                                    |  |                                 |
| - Tool Registry Lookup             |  | - Context Assembly              |
| - Argument Validation (Pydantic)   |  | - Dynamic Schema Generation     |
| - Safe Execution (Try/Except)      |  | - Grammar Constrained Sampling  |
| - State Tracking                   |  | - Response Parsing (Sum Types)  |
+------------------------------------+  +---------------------------------+
```

---

## 2. Core Architectural Decisions

### 2.1 Grammar-Constrained Decoding vs. Prompt-Based JSON
Traditional agent implementations instruct models to output raw JSON strings within conversational responses, relying on regular expressions and `json.loads()` with retry loops. On small edge models (0.5B to 7B parameters), this fails between 20% and 30% of the time due to conversational filler, markdown formatting blocks, and schema deviations.

AgentOS enforces token-level grammar sampling via `llama-cpp-python`. The dynamic JSON Schema synthesized from registered tools is compiled directly into a GBNF grammar state machine. Tokens that would generate invalid JSON syntax or invoke unregistered tools are masked at the sampler stage with a probability of $-\infty$. The syntax failure rate is zero.

### 2.2 Strict Agent-Environment Boundary
The agent orchestrator never executes Python functions or interacts with operating system interfaces directly. It issues declarative actions (`ToolAction`). The `Environment` acts as the execution sandbox and error boundary:
- All exceptions (such as missing files, division by zero, or network timeouts) are caught and serialized into structured error observations.
- The runtime never crashes on tool failures; instead, the error observation is fed back to the model, enabling autonomous self-correction.

### 2.3 Tagged Unions for Action Dispatch
Actions are modeled as discriminated sum types using Pydantic:
- `ToolAction`: Represents an intent to interact with the environment (`type="tool"`, `tool="name"`, `arguments={...}`).
- `FinalAction`: Represents goal completion (`type="final"`, `answer="..."`).

A model cannot attempt to invoke a tool and complete a task within the same step, removing state ambiguity and providing a single, clean termination condition.

### 2.4 Strategy Pattern for Decision Making
The core orchestrator depends exclusively on an abstract interface (`DecisionMaker.decide()`). This decouples the agent loop from specific model implementations:
- `QwenDecisionMaker`: Implements local inference via quantized GGUF weights.
- `FakeDecisionMaker`: A deterministic mock enabling unit test execution in under 5 milliseconds without loading model weights into RAM.

---

## 3. Codebase Structure

```
AgentOS/
├── agent/
│   ├── action.py          # Discriminated union schemas (ToolAction, FinalAction)
│   ├── action_schema.py   # Dynamic oneOf JSON Schema generation from tool definitions
│   ├── agent.py           # Core orchestrator loop with step budget and trajectory tracking
│   ├── decision.py        # Abstract base class: DecisionMaker(ABC)
│   ├── environment.py     # Execution sandbox, state tracking, and error containment
│   ├── fake_decision.py   # Deterministic mock decision maker for zero-LLM testing
│   ├── prompt.py          # Prompt assembly engine formatting tool lists and execution history
│   └── qwen_decision.py   # Concrete decision policy driving local Qwen GGUF inference
├── llm/
│   ├── __init__.py
│   └── qwen.py            # Low-level llama-cpp-python client with n_ctx=4096 and greedy decoding
├── tools/
│   ├── base.py            # Abstract tool contract requiring name, description, and Pydantic schemas
│   ├── registry.py        # Centralized tool catalog providing O(1) tool lookup and reflection
│   ├── calculator.py      # Arithmetic multiplication tool implementation
│   ├── task.py            # Task state management tool
│   ├── file_creation.py   # Filesystem tool writing content to designated paths
│   └── models.py          # Pydantic input parameter models for runtime argument validation
├── obsidian_vault/        # Interconnected technical documentation and architectural deep dives
├── main.py                # Interactive terminal REPL with rich panels, spinners, and signal handling
├── Makefile               # Automated developer tooling (run, download, clean, lint, typecheck)
└── pyproject.toml         # Dependency definitions and package configuration managed by uv
```

---

## 4. Problems Solved During Development

### 4.1 Schema Duplication in Constrained Decoding
- **Problem**: The `FinalAction` schema branch was initially appended inside the tool registration loop. If three tools were registered, the schema contained three duplicate `FinalAction` options inside `oneOf`.
- **Solution**: Refactored `agent/action_schema.py` to construct all dynamic tool branches first, appending the single `FinalAction` branch strictly outside the loop.

### 4.2 Model Context Size Misconfiguration
- **Problem**: `llm/qwen.py` passed `m_ctx=4096` to `llama_cpp.Llama`, which was ignored because the valid parameter name is `n_ctx`.
- **Solution**: Corrected the parameter to `n_ctx=4096`, ensuring the local model maintains its full context window.

### 4.3 Virtual Environment Isolation in Debuggers
- **Problem**: When running under external debuggers (such as Zed DAP / debugpy), the process executed using system Python (/usr/bin/python3) rather than the local virtual environment, causing import errors for packages installed only in `.venv`.
- **Solution**: Synchronized the project environment to Python 3.12 using `uv sync`, configured `.zed/launch.json` and `pyrightconfig.json`, and implemented a zero-dependency bootstrap import (`_bootstrap.py`) that guarantees `.venv` site-packages are injected at index 0 of `sys.path`.

### 4.4 Tool Hallucination via Identifier Mismatch (PascalCase Bug)
- **Problem**: A filesystem tool was defined with the class name identifier `CreateFile`. When provided this schema, the 0.5B model interpreted the capital casing as a Python class constructor rather than a callable tool, emitting `{"type": "final", "answer": "CreateFile(file='test.py', content='...')}` instead of generating a `ToolAction`.
- **Solution**: Standardized all tool identifiers to lowercase snake_case (`create_file`). Updated system prompts to strictly forbid simulated function calls within final answer strings.

### 4.5 Multi-Step Infinite Execution Loops (Step Amnesia)
- **Problem**: After successfully executing a tool on Step 1, the model re-evaluated the user's initial goal on Step 2. Because the prompt provided only the raw goal and current observation without execution lineage, the model forgot it had already performed the action and invoked the tool repeatedly until hitting the maximum step limit.
- **Solution**: Introduced an append-only trajectory history into `Agent.run()`. Every completed step formats the action taken and the environment observation into `EXECUTION HISTORY`. On subsequent steps, the model observes that the action has succeeded and transitions directly to `FinalAction`.

---

## 5. Current Implementation Status

- **Phase 1: Agent & Environment Foundation** (Complete)
  - Full separation between cognitive decisions and environmental side-effects.
  - Exception containment returning structured error objects.
  - O(1) dynamic tool registry.

- **Phase 2: Local Model & Constrained Decoding** (Complete)
  - Local quantized inference via `llama-cpp-python` on CPU.
  - Dynamic JSON Schema compilation to GBNF grammars.
  - Multi-step execution with trajectory history tracking.

- **Developer Tooling & Verification** (Complete)
  - Interactive terminal REPL (`main.py`) with rich formatting and exit handling.
  - Automated Makefile targets with `make check` passing flake8 and mypy cleanly across all source files.

---

## 6. Future Implementation Roadmap

### Phase 3: Durable Session & Event Sourcing
- Replace the current in-memory string list with a formal append-only event log (`agent/session.py`, `agent/events.py`).
- Implement strongly typed events:
  - `UserGoalEvent`
  - `ToolCallEvent`
  - `ToolResultEvent`
  - `FinalAnswerEvent`
- Enable session serialization to disk for pausing, replaying, and auditing multi-step executions.

### Phase 4: Reasoning Buffers (Chain of Thought)
- Expand the action schema to include an explicit reasoning field:
  ```json
  {
    "type": "tool",
    "thought": "I must first verify whether the file exists before writing.",
    "tool": "create_file",
    "arguments": { ... }
  }
  ```
- Generating reasoning tokens prior to structural arguments significantly improves tool selection accuracy in small language models.

### Phase 5: Production Tool Suite
- `FileReader`: Safe file reading with size limits and line slicing.
- `BashExecutor`: Process execution within dedicated working directories and timeout controls.
- `WebSearch`: Local search retrieval via SearXNG or DuckDuckGo API.

### Phase 6: Model Context Protocol (MCP) Integration
- Build a protocol client adapter translating between Anthropic's Model Context Protocol (MCP) and `ToolRegistry`.
- Expose external MCP servers (SQLite, GitHub, Postgres, Puppeteer) directly to the AgentOS execution loop without modifying core runtime logic.

### Phase 7: Episodic & Semantic Long-Term Memory
- Integrate vector search and BM25 hybrid retrieval to persist lessons, failure modes, and tool results across different sessions.
- Implement the Reflexion loop: after task failure, generate verbal self-reflections and store them in memory to prevent identical failure paths in future runs.

---

## 7. Installation and Verification

### Prerequisites
- Linux / macOS
- Python 3.11 or 3.12
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Setup Instructions

```bash
# 1. Clone repository
git clone <repository-url> AgentOS
cd AgentOS

# 2. Synchronize virtual environment and dependencies
uv sync

# 3. Download the quantized Qwen GGUF model (~490 MB)
make download-model

# 4. Run linter and static type analysis
make check

# 5. Launch the interactive REPL
make run
```

### Makefile Targets Reference

- `make run`: Starts the interactive AgentOS REPL.
- `make download-model`: Downloads the Qwen GGUF model using resumable curl.
- `make force-download`: Deletes existing model artifacts and redownloads from HuggingFace.
- `make clean-pycache`: Recursively purges `__pycache__`, `.mypy_cache`, and compiled `.pyc` files.
- `make flake8`: Runs Flake8 linter with a maximum line length of 100 characters.
- `make mypy`: Executes static type checking across `agent`, `llm`, `tools`, and entry points.
- `make check`: Executes both `flake8` and `mypy` in sequence.
- `make clean-model`: Removes downloaded GGUF model files from the `models/` directory.
