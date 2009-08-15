# Initialize GRAMPS Django site

update: init
	python manage.py syncdb

init: 
	python init.py > grampsdb/fixtures/initial_data.json

clean:
	rm -f gramps.sql
	rm -f *~ *.pyc *.pyo
	rm -f views/*~ views/*.pyc views/*.pyo
	rm -rf grampsdb/fixtures/initial_data.json

run:
	python manage.py runserver

sql:
	python manage.py sqlall > gramps_sql.txt
