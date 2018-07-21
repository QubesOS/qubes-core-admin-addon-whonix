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

'''qubes-core-admin extension for handling Whonix related settings'''

import qubes.ext
import qubes.vm.templatevm

class QubesWhonixExtension(qubes.ext.Extension):
    '''qubes-core-admin extension for handling Whonix related settings'''
    @qubes.ext.handler('domain-add', system=True)
    def on_domain_add(self, app, _event, vm, **_kwargs):
        '''Handle new AppVM created on whonix-ws/whonix-gw template and
        adjust its default settings
        '''
        # pylint: disable=no-self-use
        template = getattr(vm, 'template', None)
        if template is None:
            return

        if 'whonix-gw' in template.features:
            vm.tags.add('anon-gateway')

        if 'whonix-ws' in template.features:
            # this is new VM based on whonix-ws, adjust its default settings

            # look for appropriate whonix-gateway
            if 'whonix-default-gw' in template.features:
                netvm = template.features['whonix-default-gw']
            else:
                netvm = 'sys-whonix'
            if netvm in app.domains:
                vm.netvm = netvm
            else:
                # expected netvm does not exists, log an error and set netvm
                # to None
                vm.log.error('QubesWhonixExtension: netvm \'{}\' does not '
                             'exists'.format(netvm))
                vm.netvm = None

            # look for appropriate default dispvm
            if 'whonix-default-dispvm' in template.features:
                default_dispvm = template.features['whonix-default-dispvm']
            else:
                default_dispvm = template.name + '-dvm'

            if default_dispvm in app.domains:
                vm.default_dispvm = default_dispvm
            else:
                # expected default dispvm does not exists, log an error and set
                # default dispvm to None
                vm.log.error('QubesWhonixExtension: default dispvm\'{}\' does '
                             'not exists'.format(default_dispvm))
                vm.default_dispvm = None

            vm.tags.add('anon-vm')

    @qubes.ext.handler('features-request')
    def on_features_request(self, vm, _event, untrusted_features):
        '''Handle whonix-ws/whonix-gw template advertising itself'''
        # pylint: disable=no-self-use
        # Allow VM to advertise itself as whonix-ws. But do not allow to drop
        #  that info on its own
        if not isinstance(vm, qubes.vm.templatevm.TemplateVM):
            return
        if 'whonix-gw' in untrusted_features:
            vm.features['whonix-gw'] = True
            vm.tags.add('whonix-updatevm')
        if 'whonix-ws' in untrusted_features:
            vm.features['whonix-ws'] = True
            vm.tags.add('whonix-updatevm')

    @qubes.ext.handler('domain-load')
    def on_domain_load(self, vm, _event):
        '''Retroactively add tags to sys-whonix and anon-whonix'''
        # pylint: disable=no-self-use
        if vm.name == 'sys-whonix' and 'anon-gateway' not in vm.tags:
            vm.tags.add('anon-gateway')
        if vm.name == 'anon-whonix' and 'anon-vm' not in vm.tags:
            vm.tags.add('anon-vm')
