import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mini_choice",
    version="0.1",
    author="MegaBluejay",
    author_email="dmoiseev2011@gmail.com",
    description="Alternate ChoiceScript interpreter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MegaBluejay/mini_choice",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)