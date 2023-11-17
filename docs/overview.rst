.. _overview:

Overview
==========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Organizations
-------------
.. list-table::
   :widths: 60 40

   * - Get a specific organization
     - :func:`Sentry.organization() <sentrypy.sentry.Sentry.organization>`

Teams
-----
.. list-table::
   :widths: 60 40

   * - Get a specific team
     - :func:`Organization.team() <sentrypy.models.Organization.team>`
   * - Get an iterator over all teams
     - :func:`Organization.teams() <sentrypy.models.Organization.teams>`
   * - Create a new team
     - :func:`Organization.create_team() <sentrypy.models.Organization.create_team>`
   * - Delete a team
     - :func:`Team.delete() <sentrypy.models.Team.delete>`

Projects
--------
.. list-table::
   :widths: 60 40

   * - Get a specific project
     - :func:`Organization.project() <sentrypy.models.Organization.project>`
   * - Get an iterator over all projects
     - :func:`Sentry.projects() <sentrypy.sentry.Sentry.projects>`
   * - Get event counts of a project
     - :func:`Project.event_counts() <sentrypy.models.Project.event_counts>`
   * - Get all tag values of a project
     - :func:`Project.tag_values() <sentrypy.models.Project.tag_values>`


Issues
------
.. list-table::
   :widths: 60 40

   * - Get a specific issue
     - :func:`Organization.issue() <sentrypy.models.Organization.issue>`
   * - Get an interator over all or specific issues
     - :func:`Project.issues() <sentrypy.models.Project.issues>`
   * - Update a single issue
     - :func:`Issue.update() <sentrypy.models.Issue.update>`
   * - Update multiple issues
     - :func:`Project.update_issues() <sentrypy.models.Project.update_issues>`

Events
------
.. list-table::
   :widths: 60 40

   * - Get an interator over all events of an issue
     - :func:`Issue.events() <sentrypy.models.Issue.events>`

Integrations
------------
.. list-table::
   :widths: 60 40

   * - Get an iterator over all or specific integrations
     - :func:`Organization.integrations() <sentrypy.models.Organization.integrations>`