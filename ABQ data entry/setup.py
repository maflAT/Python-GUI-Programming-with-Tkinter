from setuptools import setup

with open("README.rst", "r") as fh:
    long_desc = fh.read()

setup(
    name="ABQ_Data_Entry",
    version="1.0",
    author="Alan D. Moore",
    description="Data entry application for ABQ Agrilabs",
    long_description=long_desc,
    url="http://abq.example.com",
    license="ABQ corporate license",
    packages=["abq_data_entry", "abq_data_entry.images"],
    install_requires=["psycopg2", "requests", "matplotlib"],
    python_requires=">= 3.8",
    package_data={"abq_data_entry.images": ["*.png"]},
    entry_points={"gui_scripts": ["abq = abq_data_entry:main"]},
)
