qubes-core-admin extension for handling Whonix related settings
---------------------------------------------------------------

This extension takes care of setting up Whonix Workstation base VM. When new VM
is created based on a template with `whonix-ws` feature set, it gets:
 - netvm set to `sys-whonix` (can be overriden by `whonix-default-gw` feature
   on the template)
 - default dispvm set to name of the template + `-dvm` (can be overriden by
   `whonix-default-dispvm` feature on the template)
 - tag `anon-vm` used by various qrexec policies

If any of referenced VM does not exists, extension set relevant property to
none, to not risk leaking data over clearnet.

Similarly, new Whonix Gateway is configured. When new VM is created based on a
template with `whonix-gw` feature set it gets:
 - `anon-gateway` tag

Additionally, Whonix Gateway/Workstation template can request `whonix-ws` feature to be
added to itself, easing bootstrap of this feature. The canonical way to do
this, is to place a script in `/etc/qubes/post-install.d` (with `.sh`
extension), with just one call:

    qvm-features-request whonix-gw 1

or

    qvm-features-request whonix-ws 1

This will set appropriate `whonix-gw`/`whonix-ws` feature, and also add
`whonix-updatevm` tag, so templates will be updated over Whonix Gateway.

The template cannot request the feature to be removed.
