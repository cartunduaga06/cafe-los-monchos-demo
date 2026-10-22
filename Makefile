.PHONY: dev check build publish status
dev:
	python3 scripts/dev.py
check:
	node --check app.js
	python3 -m unittest discover -s scripts -p "test_*.py"
	python3 scripts/site_tools.py check
build: check
	python3 scripts/site_tools.py build
publish:
	bash scripts/publish.sh
status:
	git status --short --branch
