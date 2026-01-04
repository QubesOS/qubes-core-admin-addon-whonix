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
import qubes.vm
import qubes.vm.templatevm


class QubesWhonixExtension(qubes.ext.Extension):
    """qubes-core-admin extension for handling Whonix related settings"""

    @staticmethod
    def set_ws_netvm(app, vm):
        """Set the default NetVM for a Whonix-Workstation qube."""
        if isinstance(vm, qubes.vm.templatevm.TemplateVM):
            return

        curr_netvm = getattr(vm, "netvm", None)

        if not curr_netvm:
            # If VM has no NetVM, assume user doesn't want one.
            netvm = None

        elif curr_netvm and curr_netvm.features.check_with_template(
            "whonix-gw", None
        ):
            # If VM's NetVM is a Gateway, use it.
            netvm = curr_netvm

        else:
            feature = vm.features.check_with_template("whonix-default-gw", None)
            if (
                feature
                and feature in app.domains
                and app.domains[feature].features.get("whonix-gw", None)
            ):
                # If any VM in template chain has the special feature, use it.
                netvm = feature
            else:
                # If all fails, use hardcoded name.
                # HARDCODED.
                netvm = "sys-whonix"

        if netvm is None:
            if getattr(vm, "netvm", None):
                vm.netvm = None
        elif netvm in app.domains:
            vm.netvm = netvm
        else:
            vm.log.error(
                "QubesWhonixExtension: netvm '%s' does not exist", netvm
            )
            vm.netvm = None

    @staticmethod
    def set_ws_dispvm(app, vm):
        """Set the default DispVM for a Whonix-Workstation qube."""

        def get_template_dispvm(
            template: qubes.vm.templatevm.TemplateVM,
        ) -> str:
            feature = vm.features.check_with_template(
                "whonix-default-dispvm", None
            )
            if (
                feature
                and feature in app.domains
                and app.domains[feature].features.get("whonix-ws", None)
            ):
                # If any VM in template chain has the special feature, use it.
                default_dispvm = feature
            elif (
                template is not None
                and (template.name + "-dvm") in app.domains
            ):
                # If we have a template, use it for assuming a name.
                default_dispvm = template.name + "-dvm"
            else:
                # If all fails, use hardcoded name.
                # HARDCODED.
                default_dispvm = "whonix-workstation-18-dvm"
            return default_dispvm

        def set_default_dispvm(vm, default_dispvm: str | None):
            if default_dispvm is None:
                if getattr(vm, "default_dispvm", None):
                    vm.default_dispvm = None
            elif default_dispvm in app.domains:
                vm.default_dispvm = default_dispvm
            else:
                vm.log.error(
                    "QubesWhonixExtension: default dispvm '%s' does not exist",
                    default_dispvm,
                )
                vm.default_dispvm = None

        if isinstance(vm, qubes.vm.templatevm.TemplateVM):
            default_dispvm = getattr(vm, "default_dispvm", None)
            if not default_dispvm:
                return
            if not default_dispvm.features.check_with_template(
                "whonix-ws", None
            ):
                set_default_dispvm(vm, get_template_dispvm(vm))
            return

        template_for_dispvms = getattr(vm, "template_for_dispvms", False)

        if template_for_dispvms and getattr(vm, "template", None):
            # If VM is a DVM and it's template has a DVM that is not a
            # Workstation, use itself for the template.
            template_default_dispvm = getattr(
                vm.template, "default_dispvm", None
            )
            if (
                template_default_dispvm
                and not template_default_dispvm.features.check_with_template(
                    "whonix-ws"
                )
            ):
                vm.template.default_dispvm = vm

        curr_default_dispvm = getattr(vm, "default_dispvm", None)

        if not curr_default_dispvm:
            # If VM has no default_dispvm, assume user doesn't want one.
            default_dispvm = None

        elif template_for_dispvms:
            # If VM is a Workstation DVM, use itself.
            default_dispvm = vm

        elif (
            curr_default_dispvm
            and curr_default_dispvm.features.check_with_template(
                "whonix-ws", None
            )
        ):
            # If VM's default_dispvm is Whonix, use it.
            default_dispvm = curr_default_dispvm

        else:
            # Standalones don't have a template, return thyself.
            template = getattr(vm, "template", vm)
            default_dispvm = get_template_dispvm(template)

        set_default_dispvm(vm, default_dispvm)

    @staticmethod
    def set_gw_dispvm(app, vm):
        """Set the default DispVM for a Whonix-Gateway qube to None if the
        current one is not a Whonix-Workstation."""
        # pylint: disable=unused-argument
        default_dispvm = getattr(vm, "default_dispvm", None)
        if not default_dispvm:
            return
        if not default_dispvm.features.check_with_template("whonix-ws", None):
            vm.default_dispvm = None

    @qubes.ext.handler("domain-add", system=True)
    def on_domain_add(self, app, _event, vm, **_kwargs):
        """Handle new AppVM created on whonix-ws/whonix-gw template and
        adjust its default settings
        """
        if not isinstance(vm, qubes.vm.LocalVM):
            return

        if vm.features.check_with_template("whonix-gw", None):
            vm.tags.add("anon-gateway")
            vm.tags.add("sdwdate-gui-server")
            self.set_gw_dispvm(app, vm)

        if vm.features.check_with_template("whonix-ws", None):
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
        Whonix-Workstation VM
        """
        # pylint: disable=unused-argument,too-many-positional-arguments
        if not value:
            return
        self.set_ws_netvm(vm.app, vm)
        self.set_ws_dispvm(vm.app, vm)

    @qubes.ext.handler("domain-feature-set:whonix-gw")
    def on_whonix_gw_feature_set(
        self,
        vm,
        event,
        feature,
        value,
        oldvalue=None,
    ):
        """Set DispVM appropriately on VMs that are newly set as a
        Whonix-Gateway VM
        """
        # pylint: disable=unused-argument,too-many-positional-arguments
        if not value:
            return
        self.set_gw_dispvm(vm.app, vm)

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
        if not isinstance(vm, qubes.vm.LocalVM):
            return

        if vm.features.check_with_template("whonix-gw", None):
            if "anon-gateway" not in vm.tags:
                vm.tags.add("anon-gateway")
            if "sdwdate-gui-server" not in vm.tags:
                vm.tags.add("sdwdate-gui-server")
        if vm.features.check_with_template("whonix-ws", None):
            if "anon-vm" not in vm.tags:
                vm.tags.add("anon-vm")
            if "sdwdate-gui-client" not in vm.tags:
                vm.tags.add("sdwdate-gui-client")
            if "gui-events-max-delay" not in vm.features:
                vm.features["gui-events-max-delay"] = 100
