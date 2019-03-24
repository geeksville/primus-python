import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="primus-python",
    version="0.0.1",
    description="A python client library for Primus compatible web servers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/geeksville/primus-python",
    author="Kevin Hester",
    author_email="kevinh@geeksville.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["ezdevice"],
    include_package_data=True,
    install_requires=["python-engineio"],
    python_requires='>=3',
    entry_points={
        "console_scripts": [
            "primus=primus.__main__:main",
        ]
    },
)
