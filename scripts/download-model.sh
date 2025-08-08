#!/usr/bin/env bash
set -e

MODEL_URL="$1"
MODEL_DIR="models"

if [ -z "$MODEL_URL" ]; then
  echo "Usage: $0 <model_url>"
  echo "Example: $0 https://huggingface.co/.../model.gguf"
  exit 1
fi

mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

if command -v wget >/dev/null 2>&1; then
  wget "$MODEL_URL"
elif command -v curl >/dev/null 2>&1; then
  curl -LO "$MODEL_URL"
else
  echo "Error: neither wget nor curl is installed" >&2
  exit 1
fi
