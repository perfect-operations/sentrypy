from setuptools import setup, find_packages

setup(
    name="sentrypy",
    version="0.1.4",
    author="Paul Weber",
    keywords="sentry api wrapper pythonic",
    description="The pythonic API wrapper for Sentry.io",
    license="LGPL-2.1",
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
            "sphinx",
            "twine",
            "wheel",
        ]
    },
    python_requires=">=3.8",
    project_urls={
        "Documentation": "https://sentrypy.readthedocs.io/en/latest/",
        "Source": "https://github.com/perfect-operations/sentrypy",
    },
)
