.PHONY: venv_create run watch install test test_watch cli deploy

BIN=venv/bin/

include .env
export

venv_create:
	virtualenv -p python3 venv

run:
	$(BIN)python handler.py

watch:
	nodemon -e py --exec "$(BIN)python handler.py"

install:
	cat requirements.txt requirements.dev.txt | $(BIN)pip install -r /dev/stdin

test:
	$(BIN)pytest --cov=handler

test_watch:
	rm -rf src/.pytest_cache &&\
	rm -rf src/.tmontmp &&\
	rm -f src/.testmondata &&\
	$(BIN)pytest-watch -- --testmon -vv --disable-pytest-warnings -rP


deploy:
	serverless deploy
