from distutils.core import setup

setup(
    name='Nikola',
    version='0.1',
    author='CZ.NIC s.z.p.o.',
    author_email='stepan.henek@nic.cz',
    packages=['nikola', 'nikola.jsonrpclib',],
    scripts=['bin/nikola',],
    url='http://pypi.python.org/pypi/Nikola-CZNIC/',
    license='LICENSE.txt',
    description='Nikola package for opewrt routers',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
