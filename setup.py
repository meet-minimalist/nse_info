##
# @author Meet Patel <>
# @file Description
# @desc Created on 2024-09-04 8:21:17 pm
# @copyright MIT License
#

from setuptools import find_packages, setup

setup(
    name="nse_info",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.9.2",
        "pandas>=2.2.2",
        "requests>=2.32.3",
        "seaborn>=0.13.2",

    ],
    entry_points={
        "console_scripts": [
            "nse_info = nse_info.main:main"
        ],
    },
    author="Meet Patel",
    # author_email='@example.com',
    description="NSE Info is a helper package which will fetch stocks information from NSE website.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/meet-minimalist/nse_info",  # URL for your package
    license="MIT",
)
