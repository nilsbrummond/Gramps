# Initialize GRAMPS Django site

update: init
	python manage.py syncdb

init: 
	python init.py > tables/fixtures/initial_data.json

clean:
	rm -f gramps.sql
	rm -f *~ *.pyc *.pyo
	rm -f views/*~ views/*.pyc views/*.pyo

run:
	python manage.py runserver
