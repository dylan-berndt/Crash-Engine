from setuptools import setup, find_packages

VERSION = '0.2.0'
DESCRIPTION = 'Python application engine'
LONG_DESCRIPTION = "A package that interfaces with pyglet for designing games using " \
                   "methods similar to Unity's design system"

setup(
    name="Crash",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="<Dylan Berndt>",
    author_email="<dylanberndt123@gmail.com>",
    license='None',
    packages=find_packages(),
    install_requires=[],
    keywords='engine',
    classifiers= [
        "Development Status :: Barely maintained",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ]
)