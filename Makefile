PYTHON ?= python
VENV   ?= venv

ACTIVATE = $(VENV)/bin/activate

install: $(VENV)
	( . $(ACTIVATE) && pip install -e .)

$(VENV):
	$(PYTHON) -m venv $@
	( . $(ACTIVATE) && pip install pytest)

tests: $(VENV)
	( . $(ACTIVATE) && pytest -v $@)

clean:
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r oratools.egg-info
	$(RM) -r venv

.PHONY: install clean tests
