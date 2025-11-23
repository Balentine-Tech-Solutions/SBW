"""
SBW CLI Tool - Setup Configuration
SBWv1.i2 Mark I Prototype
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sbw-cli",
    version="1.0.0",
    author="Demond Balentine",
    author_email="demond@balentine-tech.com",
    description="SBW CLI Tool for decoding, decrypting, and visualizing SBW log files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Balentine-Tech-Solutions/SDW",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sbw-cli=sbw_cli.main:main",
            "decode=sbw_cli.main:main",
        ],
    },
    include_package_data=True,
)