# raspi_LLM

This project provides a small Flask web application to run local LLM models via [llama.cpp](https://github.com/ggerganov/llama.cpp) using the Python bindings `llama-cpp-python`.

## Installation

The application should run on Linux, macOS and Windows. The commands below use a POSIX shell; adjust where needed for your platform.

### 1. Clone the repository
```bash
git clone https://example.com/raspi_LLM.git
cd raspi_LLM
git submodule update --init --recursive
```

### 2. Set up a virtual environment and install Python dependencies
Make sure you have a C/C++ compiler and CMake installed. On Debian/Ubuntu you can install them with:
```bash
sudo apt install build-essential cmake python3-venv
```
On macOS run `xcode-select --install` and on Windows install the *Build Tools for Visual Studio*.

Create a virtual environment and install the required packages:
```bash
python3 -m venv venv
# On Windows use: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
```
The `llama-cpp-python` package will compile `llama.cpp` for your platform during installation.

### 3. (Optional) build the standalone llama.cpp binaries
If you also want the `llama.cpp` command line tools:
```bash
cd llama.cpp
make                # or: cmake -B build && cmake --build build
cd ..
```

### 4. Download a model
Models are not bundled. Use the helper script to fetch a GGUF model into the `models/` directory:
```bash
./scripts/download-model.sh https://huggingface.co/....gguf
```
You can find many models on [Hugging Face](https://huggingface.co/). The script works with either `wget` or `curl`.

### 5. Run the server
```bash
python app.py
```
The server listens on port 5000 by default. For production you can use gunicorn:
```bash
gunicorn -w 4 -b [::]:80 --timeout 500 app:app
```

## Usage
- Visit `http://localhost:5000` in your browser.
- Available models can be queried at `/models`.
- POST questions to `/ask` with `{"question": "...", "model": "model.gguf"}`.

## Notes
The application automatically creates a `models/` directory on first run. Make sure you have enough disk space for downloaded models.
