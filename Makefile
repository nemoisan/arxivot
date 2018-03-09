.PHONY: init vendor

init: requirements.txt
	pip install -r requirements.txt

requirements.txt: requirements.in
	pip-compile --output-file $@ $<

vendor:
	pip install -U -r requirements.txt -t ./vendor
