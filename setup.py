# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from flask_restful_swagger import __version__

with open('README.md') as file:
    long_description = file.read()

setup(
    name='flask-restful-swagger',
    version=__version__,
    url='https://github.com/rantav/flask-restful-swagger',
    zip_safe=False,
    include_package_data=True,
    packages=[
        'flask_restful_swagger',
    ],
    package_data={
        'flask_restful_swagger': [
            'static/*.*',
            'static/css/*.*',
            'static/images/*.*',
            'static/lib/*.*',
            'static/lib/shred/*.*',
        ]
    },
    description='Extract swagger specs from your flast-restful project',
    author='Ran Tavory, Niall Byrne, Nikita Sobolev, Kirill Malev',
    license='MIT',
    long_description=long_description,
    install_requires=[
        'Flask-RESTful>=0.2.12',
    ],
    tests_require=[
        'pytest>=2.9.0'
    ],
    classifiers=[
        'Development Status :: 1 - Planing',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Environment :: Web Environment'
    ]

)
