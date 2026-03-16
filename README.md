# HAI-T
A lightweight terminal interface for running local LLMs — no internet, no API keys, no cloud.

HAI-T lets you load and chat with any GGUF model directly from your terminal. Built around a simple command/chat mode split, with persistent chat history, configurable inference parameters, and threaded model loading so the app stays responsive while your model initializes.

---

## Requirements
- Python 3.x
- A GGUF model file (e.g. from [HuggingFace](https://huggingface.co/models?library=gguf))
- Linux (uses `termios` for terminal input handling)

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Getting Started
1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Drop a `.gguf` model file into the `models/` folder
4. Run the app:
```bash
python app.py
```

---

## Usage
HAI-T has two modes — **command mode** (default) and **chat mode**.

In command mode, type commands to manage the app. In chat mode, type messages to talk to the loaded model. Switch between them with `chat` and `./q`.

```
> slmd          ← select and load a model
> chat          ← enter chat mode
- hello!        ← talk to the model
- ./q           ← exit chat mode
> svch          ← save the conversation
```

---

## Commands
| Command | Description |
|---|---|
| `slmd` | Select and load a model into memory |
| `mdls` | List available models |
| `rfmdls` | Refresh the model list |
| `ulmd` | Unload the current model from memory |
| `chat` | Toggle chat mode on/off |
| `svch` | Save current chat history to a file |
| `ldch` | Load a chat history from a file |
| `clch` | Clear current chat history |
| `popch` | Remove the last message from chat history |
| `shch` | Print the current chat history |
| `edconf` | Open config file in default editor |
| `dfconf` | Reset config file to defaults |
| `lsdr` | List files in the project directory |
| `lscm` | List all available commands |
| `cls` | Clear the terminal |
| `quit` | Exit the app |

In chat mode, type `./q` to return to command mode.

You can also run shell commands directly using `sys(command)` syntax, e.g. `sys(ls -la)`.

---

## Configuration
Parameters are stored in `config.json` and can be edited with `edconf` or reset with `dfconf`.

| Parameter | Default | Description |
|---|---|---|
| `context length` | 1024 | Maximum context window size |
| `max tokens` | 200 | Maximum tokens per response |
| `temperature` | 0.7 | Randomness of responses |
| `freq penalty` | 0.6 | Penalty for repeating tokens |

---

## Notes
- Model loading runs on a background thread — the app stays usable while the model initializes
- Chat history is automatically trimmed to stay within a ~6000 character context budget
- Chat histories are saved as JSON files and can be reloaded in future sessions
