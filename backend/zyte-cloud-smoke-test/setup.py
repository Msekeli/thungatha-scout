from setuptools import find_packages, setup

setup(
    name="thungatha-scout-zyte-smoke-test",
    version="0.1.0",
    packages=find_packages(),
    scripts=["bin/scout_zyte_smoke_test.py"],
    entry_points={"scrapy": ["settings=zyte_smoke_test.settings"]},
)
