clean:
	rm -rf build/ dist/

app:
	python setup.py py2app

deb:
	python setup.py py2deb

exe:
	python setup.py py2exe

html:
	make -C docs html

listimports:
	grep -r '^import' --include="*.py" * | cut -d: -f2 | sort | uniq | cut -c 8-

tests:
	python test/test_base.py
