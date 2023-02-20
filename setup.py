#!/usr/bin/env python
from os import path

from setuptools import find_packages, setup

pkg_name = "workflow_optogenetics"
here = path.abspath(path.dirname(__file__))

long_description = """"
# Workflow for optogenetics research.

Build a complete imaging workflow using the DataJoint Elements
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-event](https://github.com/datajoint/element-event)
+ [element-optogenetics](https://github.com/datajoint/element-optogenetics)
"""

with open(path.join(here, "requirements.txt")) as f:
    requirements = f.read().splitlines()

with open(path.join(here, pkg_name, "version.py")) as f:
    exec(f.read())

setup(
    name="workflow-optogenetics",
    version=__version__,  # noqa: F821
    description="Optogenetics workflow using the DataJoint elements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DataJoint",
    author_email="info@datajoint.com",
    license="MIT",
    url="https://github.com/datajoint/workflow-optogenetics",
    keywords="neuroscience datajoint optogenetics",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=requirements,
)
