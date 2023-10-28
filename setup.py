from setuptools import setup, find_packages

setup(
    name="sentrypy",
    version="0.1.1",
    author="Paul Weber",
    keywords="sentry api wrapper pythonic",
    description="The pythonic API wrapper for Sentry.io",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/perfect-operations/sentrypy",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    extras_require={
        "dev": [
            "black",
            "jupyter",
            "twine",
        ]
    },
    python_requires=">=3.8",
)
