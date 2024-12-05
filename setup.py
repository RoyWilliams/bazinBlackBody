from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))


def readme():
    with open(moduleDirectory + '/README.md') as f:
        return f.read()


setup(
    name="BazinBlackBody",
    description='Fitting multiband lightcurves with a Bazin-Blackbody surface',
    long_description=readme(),
    long_description_content_type="text/markdown",
    version="0.1",
    author='RoyDavidWilliams',
    author_email='roydavidwilliams@gmail.com',
    license='MIT',
    url='https://github.com/RoyWilliams/BBB',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
          'numpy',
          'scipy',
      ],
    classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Utilities',
    ],
    python_requires='>=3.6',
)
