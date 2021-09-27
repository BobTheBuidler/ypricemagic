from setuptools import find_packages, setup

setup(
    name='ypricemagic',
    packages=find_packages(),
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "local_scheme": "no-local-version",
        "version_scheme": "python-simplified-semver",
    },
    description='Use this tool to extract historical on-chain price data from an archive node. Shoutout to @bantg and @nymmrx for their awesome work on yearn-exporter that made this library possible.',
    author='BobTheBuidler',
    author_email='bobthebuidlerdefi@gmail.com',
    url='https://github.com/BobTheBuidler/ypricemagic',
    license='MIT',
    install_requires=[
        'cachetools>=4.1.1',
        'eth-brownie>=1.16.0',
        'joblib>=1.0.1'
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    )