PYTHON ?= python
VENV   ?= venv

$(VENV):
	$(PYTHON) -m venv $@
	$(VENV)/bin/python -m pip install pytest
	$(VENV)/bin/python -m pip install -e .

tests: $(VENV)
	$(VENV)/bin/pytest -v

clean:
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r oratools.egg-info
	$(RM) -r venv

.PHONY: install clean tests
