from setuptools import setup, find_packages
import pathlib

# Reading the long description from README.md
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="pylite",
    version="0.0.1",
    python_requires=">=3.9",
    description="An SQLite ORM for Python, inspired by Laravel's Eloquent.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/benhmoore/PyLite",
    author="Ben Moore",
    author_email="ben@benhmoore.com",
    license="MIT",  # Assuming the license in LICENSE.txt is MIT
    classifiers=[
        "Programming Language :: Python :: 3.9",
        # Add other relevant classifiers
    ],
    packages=find_packages(),  # assuming your package is organized correctly
    install_requires=["colorama"],
)
