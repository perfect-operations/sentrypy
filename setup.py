from setuptools import setup, find_packages

setup(
    name="sentrypy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    extras_require={
        "dev": [
                "black",
            "jupyter",
        ]
    },
    python_requires=">=3.8",
)
