.PHONY: setup install clean

setup:
	@echo "Setting up local environment..."
	@scripts/install_uv.sh
	@uv python install 3.11
	@scripts/create_venv.sh
	@. .venv/bin/activate && make install

install:
	@echo "Installing dependencies..."
	uv pip install fireworks-ai
	uv pip install llama-index-core
	uv pip install llama-index-llms-openai
	uv pip install pandas
	uv pip install python-dotenv
	uv pip install pillow
	uv pip install ipython

clean:
	@echo "Cleaning up..."
	rm -rf .venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} +