from setuptools import setup, find_packages

setup(
    name="flojoy",
    packages=find_packages(exclude=["tests"]),
    package_data={"flojoy": ["__init__.pyi"]},
    version="0.1.5-dev10",
    license="MIT",
    description="Python client library for Flojoy.",
    author="flojoy",
    author_email="jack.parmer@proton.me",
    url="https://github.com/flojoy-io/flojoy-python",
    download_url="https://github.com/flojoy-io/flojoy-python/archive/refs/heads/main.zip",
    keywords=[
        "data-acquisition",
        "lab-automation",
        "low-code",
        "python",
        "scheduler",
        "topic",
    ],
    python_requires=">=3.10",
    install_requires=[
        "python-box",
        "requests",
        "networkx",
        "numpy",
        "scipy",
        "pandas",
        "pytest",
        "python-dotenv",
        "pyyaml",
        "plotly==5.8.2",
        "huggingface-hub==0.16.4",
        "Pillow",
        "cloudpickle"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)
