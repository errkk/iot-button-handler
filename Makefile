.PHONY: venv_create run watch get_token install test test_watch deploy

BIN=venv/bin/

include .env
export

venv_create:
	virtualenv -p python3 venv

run:
	$(BIN)python -m handler

watch:
	nodemon -e py --exec "$(BIN)python -m handler"

get_token:
	$(BIN)python -m lib.get_token

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
