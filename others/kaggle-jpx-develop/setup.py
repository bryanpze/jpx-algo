from setuptools import find_packages, setup


setup(
    name='kaggle_jpx_package',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)
