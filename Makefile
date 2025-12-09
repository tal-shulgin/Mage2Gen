.PHONY: build test clean install refactor-tests test-local samples digest digest-samples

# Variables
IMAGE_NAME=mage2gen:latest
DDEV_CMD=~/.ddev/commands/host/m2g

help:
	@echo "Mage2Gen Development Makefile"
	@echo "-----------------------------"
	@echo "make build          - Build the Docker image"
	@echo "make test           - Run ALL tests (Unit + Integration)"
	@echo "make test-unit      - Run only Unit tests"
	@echo "make test-int       - Run only Integration tests"
	@echo "make install        - Install the global DDEV command"
	@echo "make refactor-tests - One-time script to reorganize test folder"
	@echo "make samples        - Generate 'KitchenSink' module in ./generated for review"
	@echo "make digest         - Digest SOURCE CODE (mage2gen core) -> core_tool.txt for LLM context"
	@echo "make digest-samples - Digest GENERATED CODE (./generated) -> generated-digest.txt"
	@echo "make clean          - Remove build artifacts"

# -- Host Commands --
build:
	docker build -t $(IMAGE_NAME) .

test: build
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp --entrypoint python3 -v $(PWD):/opt/mage2gen $(IMAGE_NAME) -m unittest discover -s tests -p "test_*.py" -v

test-unit: build
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp --entrypoint python3 -v $(PWD):/opt/mage2gen $(IMAGE_NAME) -m unittest discover -s tests/unit -v

test-int: build
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp --entrypoint python3 -v $(PWD):/opt/mage2gen $(IMAGE_NAME) -m unittest discover -s tests/integration -v

samples: build
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp --entrypoint python3 -v $(PWD):/opt/mage2gen $(IMAGE_NAME) scripts/generate_samples.py

# Digest the Tool Source Code (Python)
digest: build
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp --entrypoint gitingest -v $(PWD):/opt/mage2gen $(IMAGE_NAME) . -o core_tool.txt --exclude-pattern generated,*.pyc,__pycache__,test_output,.git

# Digest the Generated Magento Module (PHP/XML)
digest-samples: build
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp --entrypoint gitingest -v $(PWD):/opt/mage2gen $(IMAGE_NAME) generated -o generated-digest.txt --exclude-pattern *.pyc,__pycache__,.git

# -- Internal/Container Commands --
test-local:
	python3 -m unittest discover -s tests -p "test_*.py" -v

test-int-local:
	python3 -m unittest discover -s tests/integration -v

test-unit-local:
	python3 -m unittest discover -s tests/unit -v

refactor-tests:
	chmod +x refactor_tests.sh
	./refactor_tests.sh

install:
	mkdir -p ~/.ddev/commands/host
	@echo '#!/bin/bash' > $(DDEV_CMD)
	@echo '## Description: Global Mage2Gen Generator' >> $(DDEV_CMD)
	@echo '## Usage: m2g [command] [args]' >> $(DDEV_CMD)
	@echo 'docker run --rm -u "$$(id -u):$$(id -g)" -v "$$PWD":/output -e MAGE2GEN_OUTPUT=/output $(IMAGE_NAME) "$$@"' >> $(DDEV_CMD)
	chmod +x $(DDEV_CMD)
	@echo "✅ DDEV command installed at $(DDEV_CMD)"

clean:
	rm -rf ./generated
	rm -rf ./*.pyc
	rm -rf ./__pycache__
	rm -rf ./tests/__pycache__
	rm -rf ./tests/unit/__pycache__
	rm -rf ./tests/integration/__pycache__
	rm -f digest.txt
	rm -f generated-digest.txt