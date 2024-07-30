"""
 # @ Author: Meet Patel
 # @ Create Time: 1970-01-01 05:30:00
 # @ Modified by: Meet Patel
 # @ Modified time: 2024-07-30 19:54:43
 # @ Description:
 """

from setuptools import find_packages, setup

setup(
    name="nse_info",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List your package's dependencies here, e.g.,
        # 'numpy>=1.21.0',
    ],
    entry_points={
        "console_scripts": [
            # Define command-line scripts here if needed
        ],
    },
    # Additional metadata
    author="Meet Patel",
    # author_email='@example.com',
    description="NSE Info is a helper package which will fetch stocks information from NSE website.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/meet-minimalist/nse_info",  # URL for your package
    license="MIT",
)
