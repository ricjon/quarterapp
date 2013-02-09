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
    name='Quarterapp',
    version='0.0.1',
    author='Markus Eliasson',
    author_email='markus.eliasson@gmail.com',
    packages=['quarterapp', 'quarterapp.tests'],
    url='https://github.com/eliasson/quarterapp',
    #license=open('LICENSE').read(),
    description='Personal time management',
    #long_description=open('README.md').read(),
    install_requires=[
        "tornado >= 2.4.0"
    ],
    entry_points = {
    'console_scripts': [
        'qapp = quarterapp:main',
        ]
    },
    package_data = {'quarterapp': get_resources()},
    zip_safe = False,
)