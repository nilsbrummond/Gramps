# Initialize GRAMPS Django site

init: update
	python init.py

update:
	python manage.py syncdb

clean:
	rm -f admin.db
	rm -f *~ *.pyc *.pyo
	rm -f views/*~ views/*.pyc views/*.pyo
	rm -f databases/*~ databases/*.pyc databases/*.pyo

run:
	python manage.py runserver
