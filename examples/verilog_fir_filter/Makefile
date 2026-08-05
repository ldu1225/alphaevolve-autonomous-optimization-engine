.PHONY: help setup run

help:
	@echo "AlphaEvolve Verilog FIR Filter Example"
	@echo "  make run     - Clean previous candidates and run fresh evolution loop"

run:
	rm -rf src/candidates/*
	PYTHONPATH=../..:../../src:.:src ../../.venv/bin/python src/run_evolution.py
