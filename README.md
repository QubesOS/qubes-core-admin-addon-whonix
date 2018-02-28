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

Additionally, Whonix Workstation template can request `whonix-ws` feature to be
added to itself, easing bootstrap of this feature. The canonical way to do
this, is to place a script in `/etc/qubes/post-install.d` (with `.sh`
extension), with just one call:

    qvm-features-request whonix-ws 1

The template cannot request the feature to be removed.
