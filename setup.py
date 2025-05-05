from pathlib import Path
from setuptools import find_packages, setup


with open("requirements.txt", "r") as f:
    requirements = list(map(str.strip, f.read().split("\n")))[:-1]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


try:
    from mypyc.build import mypycify

    ext_modules = mypycify(
        [
            "y/_db/utils/stringify.py",
            "y/convert.py",
            "y/prices/utils/sense_check.py",
            "--strict",
            "--pretty",
            "--install-types",
        ]
    )
except ImportError:
    ext_modules = []

setup(
    name="ypricemagic",
    packages=find_packages(exclude=["tests", "tests.*"]),
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "local_scheme": "no-local-version",
        "version_scheme": "python-simplified-semver",
    },
    description="Use this tool to extract historical on-chain price data from an archive node. Shoutout to @bantg and @nymmrx for their awesome work on yearn-exporter that made this library possible.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BobTheBuidler",
    author_email="bobthebuidlerdefi@gmail.com",
    url="https://github.com/BobTheBuidler/ypricemagic",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    setup_requires=["setuptools_scm"],
    install_requires=requirements,
    package_data={"y": ["py.typed"]},
    include_package_data=True,
    ext_modules=ext_modules,
    zip_safe=False,
)
