from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in hotel_management/__init__.py
from hotel_management import __version__ as version

setup(
	name="hotel_management",
	version=version,
	description="Complete Hotel Management ERP System for Frappe v15",
	author="Aly Zoogy",
	author_email="alyerpnext@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
	python_requires=">=3.10",
)
