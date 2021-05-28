import setuptools


setuptools.setup(
    name="stores",
    version="0.0.0",
    author="Malmgrek",
    author_email="foo.bar@email.com",
    description="Clients for various data APIs",
    url="https://github.com/malmgrek/pandas-datastores",
    packages=["stores"],
    install_requires=[
        "attrs",
        "numpy",
        "pandas"
    ],
    keywords=[
        "RESTful APIs",
        "Open data",
    ],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ]
)
