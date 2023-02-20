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

# # DataJoint configuration
#
# ## Setup - Working Directory
#
# To run the workflow, we need to properly set up the DataJoint configuration. The configuration can be saved in a local directory as `dj_local_conf.json` or at your root directory as a hidden file. This notebook walks you through the setup process.
#
# **The configuration only needs to be set up once**, if you have gone through the configuration before, directly go to [02-workflow-structure](02-workflow-structure-optional.ipynb).
#

# +
import os

import datajoint as dj

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")

# -

# ## Setup - Credentials
#
# Now let's set up the host, user and password in the `dj.config` global variable
#

# +
import getpass

dj.config["database.host"] = "{YOUR_HOST}"  # CodeBook users should omit this
dj.config["database.user"] = "{YOUR_USERNAME}"
dj.config["database.password"] = getpass.getpass()  # enter the password securily

# -

# You should be able to connect to the database at this stage.
#

dj.conn()


# ## Setup - `dj.config['custom']`
#
# The major component of the current workflow is Element Optogenetics (see [GitHub repository](https://github.com/datajoint/element-optogenetics) and [documentation](https://datajoint.com/docs/elements/element-optogenetics)). Many Elements require configurations in the field `custom` in `dj.config`:
#
# ### Database prefix
#
# Giving a prefix to schemas could help when configuring database privileges. If we set the prefix to `neuro_`, every schema created with the current workflow will start with `neuro_`, e.g. `neuro_lab`, `neuro_subject`, etc.
#
# The prefix could be configurated to your username in `dj.config` as follows.
#

username_as_prefix = dj.config["database.user"] + "_"
dj.config["custom"] = {"database.prefix": username_as_prefix}

# ## Save configuration
#
# We could save this as a file, either as a local json file, or a global file. Local configuration file is saved as `dj_local_conf.json` in current directory, which is great for project-specific settings.
#
# For first-time users, we recommend saving globally. This will create a hidden configuration file in your root directory, which will be loaded whenever there is no local version to override it.
#

# dj.config.save_local()
dj.config.save_global()


# ## Next Step
#
# After the configuration, we will be able to run through the workflow with the [02-workflow-structure](02-workflow-structure-optional.ipynb) notebook.
#
