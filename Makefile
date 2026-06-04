.PHONY: help install run-server dummy test-client clean

# Default target: display help
help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies using uv sync"
	@echo "  make run-server    - Start the FastAPI server using uv run"
	@echo "  make dummy         - Generate dummy Chinese audio file"
	@echo "  make test-client   - Run the WebSocket test client"
	@echo "  make clean         - Remove dummy audio files and python cache directories"

# Sync dependencies
install:
	uv sync

# Run the FastAPI server
run-server:
	uv run uvicorn server:app --host 127.0.0.1 --port 9000 --reload

# Generate dummy Chinese WAV audio
dummy:
	uv run generate_dummy.py

# Run the websocket test client
test-client:
	uv run test_client.py

# Clean generated files and Python caches
clean:
	rm -f *.wav
	find . -type d -name "__pycache__" -exec rm -rf {} +
