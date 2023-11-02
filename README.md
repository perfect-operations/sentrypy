# Quickstart

[![Documentation Status](https://readthedocs.org/projects/sentrypy/badge/?version=latest)](https://sentrypy.readthedocs.io/en/latest/?badge=latest)
![black passing](https://github.com/perfect-operations/sentrypy/actions/workflows/black.yml/badge.svg)
![pytest passing](https://github.com/perfect-operations/sentrypy/actions/workflows/pytest.yml/badge.svg)
![PyPI - Version](https://img.shields.io/pypi/v/sentrypy)
![PyPI - License](https://img.shields.io/pypi/l/sentrypy)

[Sentry.io](https://sentry.io/) is an error tracking platform that helps you monitor and
resolve issues in real-time.

[sentrypy](https://github.com/perfect-operations/sentrypy) is a Python wrapper for
the Sentry API to:

- Retrieve error data
- Automate incident responses
- Integrate with your workflow

## Installation

First create a sentry token ([official tutorial](https://docs.sentry.io/api/guides/create-auth-token/)).

Then install by one of the options below.

##### Installing from PyPI
```
pip install sentrypy
```

##### Installing from source
```
git clone git@github.com:perfect-operations/sentrypy.git
pip install -e sentrypy
```

## Usage

```python
from sentrypy.sentry import Sentry

# Connect to Sentry API
sentry = Sentry(token="your_secret_token")

# Retrieve a project
project = sentry.project(organization_slug="your_org", project_slug="your_project")

# Inspect the issues
for issue in project.issues():
    print(issue.title)
```
Example output:
```
IndexError: list index out of range
WebDriverException: Message: unknown error: session deleted because of page crash
AttributeError: 'NoneType' object has no attribute 'startswith'
```

Do this and much more. Install and explore!

## Documentation
Read the full documentation [on ReadTheDocs](https://sentrypy.readthedocs.io/en/latest/).

## Feature Requests & Issues
Please let me know [here on GitHub](https://github.com/perfect-operations/sentrypy/issues)!

## Support
* Write me [on Twitter](https://twitter.com/drpaulw)
* Write me [on LinkedIn](https://www.linkedin.com/in/drpaulw)
