all:
	python3 setup.py build

install:
	# force /usr/bin before /bin to have /usr/bin/python instead of /bin/python
	PATH="/usr/bin:$$PATH" python3 setup.py install $(PYTHON_PREFIX_ARG) -O1 --skip-build --root $(DESTDIR)

