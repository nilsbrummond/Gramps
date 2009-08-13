# Initialize GRAMPS Django site

init: update
	python init.py

update:
	python manage.py syncdb

clean:
	rm -f gramps.sql
	rm -f *~ *.pyc *.pyo
	rm -f views/*~ views/*.pyc views/*.pyo

run:
	python manage.py runserver
