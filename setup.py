from setuptools import find_packages, setup

requirements = """
arrow
click
requests
simple_term_menu
pandas
matplotlib
"""

setup(
    name="nbp_rates",
    author="Wojciech Nowak",
    author_email="mail@pythonic.ninja",
    description="{description}",
    packages=find_packages(),
    test_suite="tests",
    install_requires=requirements,
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    zip_safe=False,
    # all functions @cli.command() decorated in edf_re_aos_pkg/cli.py
    entry_points={
        "console_scripts": ["nbp_rates = nbp_rates.cli:main"]
    },
)
