import setuptools
from pss1830exec.__version__ import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pssexec",
    version=VERSION,
    author="Trung Truong",
    author_email="trungdtbk@gmail.com",
    description="Run CLI/root commands on a Nokia 1830-PSS NE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trungdtbk/nokia-1830pss-exec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Topic :: System :: Networking",

    ],
    entry_points={
        'console_scripts' : ['pssexec=pss1830exec.pssexec:main']
    },
    install_requires=[
        'nokia1830pss == 1.0.3'
    ]
)