# -*- coding: utf-8 -*-
#quickstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       None
#
#

#This is just a work-around for a Python2.7 issue causing
#interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=[]
install_requires=[]

import simviz as this_package

name = this_package.__name__
version = this_package.__version__
author = this_package.__author__
email = this_package.__email__
url = this_package.__url__
    
setup(
    name=name,
    version=version,
    description='',
    author=author,
    author_email=email,
    url=url,
    setup_requires=[],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'simviz': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'development.ini',
                                 'public/*/*/*/*/*/*/*/*/*/*']},
    message_extractors={'simviz': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = simviz.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    dependency_links=[
        "http://tg.gy/222"
        ],
    zip_safe=False
)
