# -*- encoding: utf-8 -*-
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2018 Marek Marczykowski-Górecki
#                               <marmarek@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

"""qubes-core-admin extension for handling Whonix related settings"""

import qubes.ext
import qubes.vm.templatevm


class QubesWhonixExtension(qubes.ext.Extension):
    """qubes-core-admin extension for handling Whonix related settings"""

    @staticmethod
    def set_ws_netvm(app, vm):
        """Set the default NetVM for a Whonix-Workstation qube."""
        if isinstance(vm, qubes.vm.templatevm.TemplateVM):
            return
        template = getattr(vm, "template", None)
        # look for appropriate whonix-gateway
        if template is not None and "whonix-default-gw" in template.features:
            netvm = template.features["whonix-default-gw"]
        else:
            netvm = "sys-whonix"
        if netvm in app.domains:
            vm.netvm = netvm
        else:
            # expected netvm does not exists, log an error and set netvm
            # to None
            vm.log.error(
                "QubesWhonixExtension: netvm '%s' does not " "exists", netvm
            )
            vm.netvm = None

    @staticmethod
    def set_ws_dispvm(app, vm):
        """Set the default DispVM for a Whonix-Workstation qube."""
        if isinstance(vm, qubes.vm.templatevm.TemplateVM):
            return
        template = getattr(vm, "template", None)
        # look for appropriate default dispvm
        if (
            template is not None
            and "whonix-default-dispvm" in template.features
        ):
            default_dispvm = template.features["whonix-default-dispvm"]
        elif template is not None:
            #  example template.name: whonix-ws-14
            # example default_dispvm: whonix-ws-14-dvm
            default_dispvm = template.name + "-dvm"
        else:
            # assume whonix-workstation-17-dvm is right
            # HARDCODED.
            default_dispvm = "whonix-workstation-17-dvm"

        if default_dispvm in app.domains:
            vm.default_dispvm = default_dispvm
        else:
            # expected default dispvm does not exists, log an error and set
            # default dispvm to None
            vm.log.error(
                "QubesWhonixExtension: default dispvm'%s' does " "not exists",
                default_dispvm,
            )
            vm.default_dispvm = None

    @qubes.ext.handler("domain-add", system=True)
    def on_domain_add(self, app, _event, vm, **_kwargs):
        """Handle new AppVM created on whonix-ws/whonix-gw template and
        adjust its default settings
        """
        template = getattr(vm, "template", None)
        if template is None:
            return

        if "whonix-gw" in template.features:
            vm.tags.add("anon-gateway")
            vm.tags.add("sdwdate-gui-server")

        if "whonix-ws" in template.features:
            # this is new VM based on whonix-ws, adjust its default settings

            vm.tags.add("anon-vm")
            vm.tags.add("sdwdate-gui-client")

            self.set_ws_netvm(app, vm)
            self.set_ws_dispvm(app, vm)

            if "gui-events-max-delay" not in vm.features:
                vm.features["gui-events-max-delay"] = 100

    @qubes.ext.handler("domain-feature-set:whonix-ws")
    def on_whonix_ws_feature_set(
        self,
        vm,
        event,
        feature,
        value,
        oldvalue=None,
    ):
        """Set NetVM and DispVM appropriately on VMs that are newly set as a
        Whonix-Workstation VM (mostly useful for configuring StandaloneVMs
        """
        # pylint: disable=unused-argument,too-many-positional-arguments
        if value == "1":
            self.set_ws_netvm(vm.app, vm)
            self.set_ws_dispvm(vm.app, vm)

    @qubes.ext.handler("features-request")
    def on_features_request(self, vm, _event, untrusted_features):
        """Handle whonix-ws/whonix-gw template advertising itself"""
        # Allow VM to advertise itself as whonix-ws. But do not allow to drop
        #  that info on its own
        if not isinstance(vm, qubes.vm.templatevm.TemplateVM):
            return
        if "whonix-gw" in untrusted_features:
            vm.features["whonix-gw"] = True
            vm.tags.add("whonix-updatevm")
        if "whonix-ws" in untrusted_features:
            vm.features["whonix-ws"] = True
            vm.tags.add("whonix-updatevm")

    @qubes.ext.handler("domain-load")
    def on_domain_load(self, vm, _event):
        """Retroactively add tags to sys-whonix and anon-whonix. Also enable
        event buffering if it's not already enabled.
        """
        if hasattr(vm, "template") and "whonix-gw" in vm.template.features:
            if "anon-gateway" not in vm.tags:
                vm.tags.add("anon-gateway")
            if "sdwdate-gui-server" not in vm.tags:
                vm.tags.add("sdwdate-gui-server")
        if hasattr(vm, "template") and "whonix-ws" in vm.template.features:
            if "anon-vm" not in vm.tags:
                vm.tags.add("anon-vm")
            elif "sdwdate-gui-client" not in vm.tags:
                vm.tags.add("sdwdate-gui-client")
        if (
            hasattr(vm, "template")
            and "whonix-ws" in vm.template.features
            and "gui-events-max-delay" not in vm.features
        ):
            vm.features["gui-events-max-delay"] = 100
