from setuptools import find_packages, setup

setup(
    name='vedirect',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version'],
    url='https://juju.nz/src/michaelh/vedirect',
    author='Michael Hope',
    author_email='michaelh@juju.nz',
    description='VE.Direct parser and exporter',
    zip_safe=True,
    packages=find_packages(),
    install_requires=[
        'Pint>=0.16.1',
        'click>=7.1.2',
        'paho-mqtt>=1.5.1',
        'prometheus-client>=0.8.0',
        'pyserial>=3.4',
    ],
    entry_points='''
[console_scripts]
vedirect=vedirect.cli:app
    ''',
)
