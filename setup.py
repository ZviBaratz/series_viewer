import os
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements/common.txt") as fh:
    requirements = fh.read().splitlines()

with open("requirements/dev.txt") as fh:
    dev_requirements = fh.read().splitlines()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="series_viewer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A bokeh application to view 2D slices from a 3D matrix.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZviBaratz/series_viewer",
    author="Zvi Baratz",
    author_email="z.baratz@gmail.com",
    keywords="bokeh mri neuroimaging research",
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Researchers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
)
