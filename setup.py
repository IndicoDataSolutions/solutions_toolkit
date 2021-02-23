import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="indico-solutions-toolkit",
    version="0.0.1",
    description="Modules for Indico Integration",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/IndicoDataSolutions/solutions_toolkit",
    author="Andrew Fitzgerald",
    author_email="andrew.fitzgerald@indico.io",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["indico-client==4.5.0", "PyYAML", "tqdm"],
)
