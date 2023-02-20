# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.9.13 ('ele')
#     language: python
#     name: python3
# ---

# # Introduction to the workflow structure
#
# This notebook gives a brief overview of the workflow structure and introduces some useful DataJoint tools to facilitate the exploration.
#
# - DataJoint needs to be pre-configured before running this notebook, if you haven't set up the configuration, refer to notebook [01-configure](01-configure.ipynb).
#
# - If you are familar with DataJoint and the workflow structure, proceed to the next notebook [03-process](03-process.ipynb) directly to run the workflow.
#
# - For a more thorough introduction of DataJoint functionality, please visit our [Elements user guide](https://datajoint.com/docs/elements/user-guide/) and [general documentation](https://datajoint.com/docs/core/concepts/mantra/)
#
# To load the local configuration, we will change the directory to the package root.
#

# +
import os

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")

# -

# ## Schemas and tables
#
# The current workflow is composed of multiple database schemas, each of them corresponds to a module within `workflow_optogenetics.pipeline`
#

import datajoint as dj

from workflow_optogenetics.pipeline import Device, lab, opto, session, subject, surgery

# Each module contains a schema object that enables interaction with the schema in the database.
#

# + Each module imported above corresponds to one schema inside the database. For example, `ephys` corresponds to `neuro_ephys` schema in the database.
opto.schema

# -

# The table classes in the module corresponds to a table in the schema in the database.
#

# + Each datajoint table class inside the module corresponds to a table inside the schema. For example, the class `ephys.EphysRecording` correponds to the table `_ephys_recording` in the schema `neuro_ephys` in the database.
# preview columns and contents in a table
opto.OptoWaveform()


# + The first time importing the modules, empty schemas and tables will be created in the database. [markdown]
# By importing the modules for the first time, the schemas and tables will be created inside the database.
#
# Once created, importing modules will not create schemas and tables again, but the existing schemas/tables can be accessed and manipulated by the modules.
#
# + The schemas and tables will not be re-created when importing modules if they have existed. [markdown]
# ## DataJoint tools to explore schemas and tables
#
# `dj.list_schemas()`: list all schemas a user has access to in the current database
#
# + `dj.list_schemas()`: list all schemas a user could access.
dj.list_schemas()

# -

# `dj.Diagram()`: plot tables and dependencies in a schema. See also [diagram notation docs](https://datajoint.com/docs/core/concepts/getting-started/diagrams/).
#

# + `dj.Diagram()`: plot tables and dependencies
# Plot diagram for all tables in a schema
dj.Diagram(opto)


# + `dj.Diagram()`: plot the diagram of the tables and dependencies. It could be used to plot tables in a schema or selected tables.
# Plot diagram of tables in multiple schemas.
# Adding and subtracting looks downstream and upstream respectively
dj.Diagram(surgery) + dj.Diagram(opto) - 1

# -

# Plot diagram of selected tables and schemas
(
    dj.Diagram(subject.Subject)
    + dj.Diagram(session.Session)
    + dj.Diagram(surgery.Implantation)
    + dj.Diagram(opto.OptoProtocol)
)


# + `heading`: [markdown]
# `describe()`: show table definition with foreign key references.
#
# -
opto.OptoProtocol.describe()


# `heading`: show attribute definitions regardless of foreign key references
#

# + `heading`: show table attributes regardless of foreign key references.
opto.OptoProtocol.heading


# + ephys [markdown]
# ## Elements in `workflow-optogenetics`
#
# [`lab`](https://datajoint.com/docs/elements/element-animal/): lab management related information, such as Lab, User, Project, Protocol, Source.
#
# -

dj.Diagram(lab)


# [`subject`](https://datajoint.com/docs/elements/element-animal/): general animal metadata and surgery information

dj.Diagram(subject)


# + [subject](https://github.com/datajoint/element-animal): contains the basic information of subject, including Strain, Line, Subject, Zygosity, and SubjectDeath information.
subject.Subject.describe()

# -

dj.Diagram(surgery)

# [`session`](https://datajoint.com/docs/elements/element-session/): General information of experimental sessions.
#

dj.Diagram(session)


# + [session](https://github.com/datajoint/element-session): experimental session information
session.Session.describe()

# -

# [`opto`](https://github.com/datajoint/element-optogenetics): Optogenetics stimulus and timing data
#

# + [probe and ephys](https://github.com/datajoint/element-array-ephys): Neuropixel based probe and ephys tables
dj.Diagram(opto)

# -

# ## Summary and next step
#
# - This notebook introduced the overall structures of the schemas and tables in the workflow and relevant tools to explore the schema structure and table definitions.
#
# - In the next notebook [03-process](03-process.ipynb), we will introduce the detailed steps to run through `workflow-optogenetics`.
#
