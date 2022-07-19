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
        'async_lru==1.0.3',
        'async_property==0.2.1',
        'bobs_lazy_logging==0.0.4',
        'cachetools>=4.1.1',
        'dank_mids==0.1.0',
        'eth-brownie>=1.18.1,<1.19',
        'eth_retry>=0.1.5,<0.2',
        'joblib>=1.0.1',
        'multicall>=0.5.1,<0.6',
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    )