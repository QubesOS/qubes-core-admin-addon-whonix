# vim: fileencoding=utf-8

import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='qubeswhonix',
        version=open('version').read().strip(),
        author='Invisible Things Lab',
        author_email='marmarek@invisiblethingslab.com',
        description='Qubes Whonix core-admin extension',
        license='GPL2+',
        url='https://www.qubes-os.org/',

        packages=('qubeswhonix',),

        entry_points={
            'qubes.ext': [
                'qubeswhonix = qubeswhonix:QubesWhonixExtension',
            ],
        }
    )
