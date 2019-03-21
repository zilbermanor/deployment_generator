import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="v3io_generator",
    version="0.0.25dev",
    author="Or Zilberman",
    author_email="zilbermanor@gmail.com",
    description="Fake deployment and data generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zilbermanor/deployment_generator",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)