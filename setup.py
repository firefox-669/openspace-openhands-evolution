from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openspace-openhands-evolution",
    version="0.1.0",
    author="OpenSpace Team",
    description="Self-Evolving AI Programming Assistant System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/openspace-openhands-evolution",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.12",
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        'console_scripts': [
            'openspace-evolution=openspace_openhands_evolution.__main__:run_main',
        ],
    },
)
