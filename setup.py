from distutils.core import setup
import os.path

def get_resources():
    resources = []
    def assembler(arg, folder, files):
        if folder:
            resources.append(folder[len('quarterapp/'):] + '/*.*')
    os.path.walk('quarterapp/resources', assembler, True)
    return resources

setup(
    name='quarterapp',
    version='0.0.3',
    author='Markus Eliasson',
    author_email='markus.eliasson@gmail.com',
    packages=['quarterapp', 'quarterapp.tests'],
    url='https://github.com/eliasson/quarterapp',
    license="BSD license",
    description='Personal time management',
    install_requires=[
        "tornado >= 2.4.0"
    ],
    entry_points = {
    'console_scripts': [
        'quarterapp = quarterapp:main',
        ]
    },
    package_data = {'quarterapp': get_resources()},
    zip_safe = False,
)