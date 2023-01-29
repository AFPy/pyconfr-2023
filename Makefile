.venv:
	python3 -m venv .venv
	.venv/bin/pip install frozen-flask libsass markdown2 beautifulsoup4 icalendar python-slugify

install: .venv

static: .venv
	FLASK_APP=pyconfr.py .venv/bin/flask freeze

serve: .venv
	@echo -e "\nHome page available at \033[0;32mhttp://localhost:5000/\033[0m\n"
	FLASK_APP=pyconfr.py FLASK_DEBUG=1 .venv/bin/flask run

serve-static: .venv
	@echo -e "\nHome page available at \033[0;33mhttp://localhost:8000/index.html\033[0m\n"
	.venv/bin/python -m http.server 8000 -d build

deploy: static
	rsync -vazh --delete build/2023/ pyconfr@deb2.afpy.org:/var/www/pycon.fr/2023/

clean:
	rm -rf build .venv __pycache__

.PHONY: install static serve serve-static deploy clean
