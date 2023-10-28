# `sentrypy` Quickstart

[Sentry.io](https://sentry.io/) is an error tracking platform that helps you monitor and
resolve issues in real-time.

[sentrypy](https://github.com/perfect-operations/sentrypy) is a Python wrapper for
the Sentry API to:

- Retrieve error data
- Automate incident responses
- Integrate with your workflow

## Prerequisites

- Sentry API token →[official tutorial](https://docs.sentry.io/api/guides/create-auth-token/)

## Installation

`pip install sentrypy`

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
## Bonus
This is an early stage project. Your ideas are welcome!
