try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='flask-restful-swagger',
      version='0.1',
      url='https://github.com/rantav/flask-restful-swagger',
      packages=['flask_restful_swagger'],
      description='Extrarct swagger specs from your flast-restful project',
      author='Ran Tavory',
      license='MIT',
      install_requires=['Flask-RESTful>=0.2.4']
      )
