from distutils.core import setup

setup(
    name='Quarterapp',
    version='0.0.1',
    author='Markus Eliasson',
    author_email='markus.eliasson@gmail.com',
    packages=['quarterapp', 'quarterapp.test'],
    scripts=['bin/quarterapp.py'],
    url='https://github.com/eliasson/quarterapp',
    license='LICENSE',
    description='Personal time management',
    long_description=open('README.md').read(),
    install_requires=[
        "tornado >= 2.4.0"
    ],
)