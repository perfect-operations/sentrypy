.. _quickstart:

Quickstart
==========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Get all issues of a project
---------------------------

.. code-block:: python

    from sentrypy import Sentry

    # Connect to sentry, get organization and project
    sentry = Sentry(token="your-token")
    org = sentry.organization("your-organization-slug")
    project = org.project("your-project-slug")

    # Iterate over all issues of project
    for issue in project.issues():
        print(issue.title)
