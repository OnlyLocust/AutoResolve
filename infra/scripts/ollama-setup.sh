#!/bin/bash
# Run once before starting Day 1 dev work.
# The llama3.1:8b model download is 4.7GB.
set -e

echo "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

echo "Starting Ollama service in background..."
ollama serve &
OLLAMA_PID=$!
sleep 5

echo "Pulling llama3.1:8b (4.7GB — takes several minutes)..."
ollama pull llama3.1:8b

echo "Creating custom DeployBrain model from Modelfile..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ollama create deploybrain -f "$SCRIPT_DIR/Modelfile"

echo ""
echo "✅ Ollama setup complete."
echo "   Test with: ollama run deploybrain"
echo "   Stop server: kill $OLLAMA_PID"

wait $OLLAMA_PID