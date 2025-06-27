from pathlib import Path
from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.read().splitlines() if line.strip()]

try:
    from mypyc.build import mypycify

    ext_modules = mypycify(
        [
            "y/_db/decorators.py",
            "y/_db/utils/stringify.py",
            "y/_db/config.py",
            "y/ENVIRONMENT_VARIABLES.py",
            "y/convert.py",
            "y/exceptions.py",
            "y/networks.py",
            "y/prices/utils/sense_check.py",
            "y/utils/gather.py",
            "--pretty",
            "--install-types",
            "--disable-error-code=import-not-found",
            "--disable-error-code=import-untyped",
            "--disable-error-code=no-any-return",
            "--disable-error-code=misc",
            "--disable-error-code=attr-defined",
            "--disable-error-code=return-value",
            "--disable-error-code=operator",
            "--disable-error-code=override",
            "--disable-error-code=call-arg",
            "--disable-error-code=union-attr",
            "--disable-error-code=str-bytes-safe",
            "--disable-error-code=call-overload",
            "--disable-error-code=used-before-def",
            "--disable-error-code=return",
            "--disable-error-code=index",
            "--disable-error-code=list-item",
            "--disable-error-code=annotation-unchecked",
            "--disable-error-code=empty-body",
            "--disable-error-code=has-type",
            "--disable-error-code=no-redef",
            "--disable-error-code=valid-type",
            "--disable-error-code=assignment",
            "--disable-error-code=arg-type",
            "--disable-error-code=var-annotated",
            "--disable-error-code=typeddict-item",
            "--disable-error-code=type-var",
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
    python_requires=">=3.9,<3.13",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
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
    entry_points={"console_scripts": ["ypricemagic=y.cli:main"]},
    ext_modules=ext_modules,
    zip_safe=False,
)
