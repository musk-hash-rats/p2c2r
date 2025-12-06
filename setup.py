"""Setup configuration for P2C2G package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="p2c2g",
    version="0.1.0",
    author="musk-hash-rats",
    author_email="",
    description="A distributed computing framework for cloud gaming sessions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/musk-hash-rats/p2c2r",
    project_urls={
        "Bug Tracker": "https://github.com/musk-hash-rats/p2c2r/issues",
        "Documentation": "https://github.com/musk-hash-rats/p2c2r/blob/main/docs/",
        "Source Code": "https://github.com/musk-hash-rats/p2c2r",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for the PoC
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "p2c2g=p2c2g.__main__:main",
        ],
    },
)
