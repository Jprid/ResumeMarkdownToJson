from setuptools import setup, find_packages

setup(
    name="resumemodule",
    version="0.1.0",
    description="A module for processing resume markdown files to JSON and HOCON.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pyhocon"
    ],
    entry_points={
        "console_scripts": [
            "resume-process = resumemodule.__main__:ResumeProcessor"
        ]
    },
    python_requires=">=3.7",
)
