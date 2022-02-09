all:
	python3 setup.py build

install:
	# force /usr/bin before /bin to have /usr/bin/python instead of /bin/python
	PATH="/usr/bin:$$PATH" python3 setup.py install $(PYTHON_PREFIX_ARG) -O1 --skip-build --root $(DESTDIR)
	mkdir -p $(DESTDIR)/etc/qubes-rpc/policy
	cp qubes-rpc-policy/whonix.GatewayCommand.policy $(DESTDIR)/etc/qubes-rpc/policy/whonix.GatewayCommand
	cp qubes-rpc-policy/whonix.NewStatus.policy $(DESTDIR)/etc/qubes-rpc/policy/whonix.NewStatus
	cp qubes-rpc-policy/whonix.SdwdateStatus.policy $(DESTDIR)/etc/qubes-rpc/policy/whonix.SdwdateStatus
	mkdir -p $(DESTDIR)/etc/qubes/policy.d/
	cp qubes-rpc-policy/80-whonix.policy $(DESTDIR)/etc/qubes/policy.d/80-whonix.policy
