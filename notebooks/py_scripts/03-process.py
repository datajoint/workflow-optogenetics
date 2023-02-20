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

# # Interactively run workflow optogenetics
#
# - This notebook walks you through the steps in detail to run the `workflow-optogenetics`.
#
# - If you haven't configured the paths, refer to [01-configure](01-configure.ipynb).
#
# - To overview the schema structures, refer to [02-workflow-structure](02-workflow-structure.ipynb).
#
# - For a more thorough introduction of DataJoint functionality, please visit our [Elements user guide](https://datajoint.com/docs/elements/user-guide/) and [general documentation](https://datajoint.com/docs/core/concepts/mantra/).
#

# Let's change the directory to the package root directory to load the local configuration (`dj_local_conf.json`).
#

# +
import os

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")

# -

# ## `pipeline.py`
#
# This script `activates` the DataJoint Elements and declares other required tables.
#

import datajoint as dj

from workflow_optogenetics.pipeline import Device, lab, opto, session, subject, surgery

# ## Schema diagrams
#
# See also [diagram notation docs](https://datajoint.com/docs/core/concepts/getting-started/diagrams/).
#

(
    dj.Diagram(subject.Subject)
    + dj.Diagram(session.Session)
    + dj.Diagram(surgery.Implantation)
    + dj.Diagram(opto)
)


# ## Inserting data
#

# ### `lab` schema
#
# `pipeline.py` adds a Device table to the `lab` schema. This table, like other `Lookup` tables, has default contents, but we can always add more.
#

Device.insert1(
    dict(
        device="OPTG_8",
        modality="Optogenetics",
        description="8 channel pulse sequence device",
    )
)


lab.User.insert1(
    dict(user="User1")
)  # For the surgeon attribute in surgery.Implantation


# ### `subject` schema
#

subject.Subject.heading


subject.Subject.insert1(
    dict(
        subject="subject3",
        sex="F",
        subject_birth_date="2020-03-03",
        subject_description="Optogenetic pilot subject.",
    )
)


# In order to conduct optogenetic stimulation, our subject must have an implant in the target brain region. Again, some `Lookup` tables have useful default content.
#

surgery.CoordinateReference()


surgery.Hemisphere()


# +
surgery.BrainRegion.insert1(
    dict(region_acronym="dHP", region_name="Dorsal Hippocampus")
)
surgery.Implantation.insert1(
    dict(
        subject="subject3",
        implant_date="2022-04-01 12:13:14",
        implant_type="opto",
        target_region="dHP",
        target_hemisphere="left",
        surgeon="user1",
    )
)

surgery.Implantation.Coordinate.insert1(
    dict(
        subject="subject3",
        implant_date="2022-04-01 12:13:14",
        implant_type="opto",
        target_region="dHP",
        target_hemisphere="left",
        ap="-7.9",  # anterior-posterior distance in mm
        ap_ref="bregma",
        ml="-1.8",  # medial axis distance in mm
        ml_ref="bregma",
        dv="5",  # dorso-ventral axis distance in mm
        dv_ref="skull_surface",
        theta="11.5",  # degree rotation about ml-axis [0, 180] wrt z
        phi="0",  # degree rotation about dv-axis [0, 360] wrt x
        beta=None,  # degree rotation about shank [-180, 180] wrt anterior
    )
)

# -

# ### Insert into `session` schema
#

session.Session.describe()


session.Session.heading


session_key = dict(
    subject="subject3", session_id="1", session_datetime="2022-04-04 12:13:14"
)
session.Session.insert1(session_key)
session.Session()


# ### Insert into `opto` schema
#

# First, we'll add information to describe the stimulus, including waveform shape and and application parameters.
#

opto.OptoWaveform.insert1(
    dict(
        waveform_name="square_10",
        waveform_type="square",
        waveform_description="Square waveform: 10%/90% on/off cycle",
    )
)
# Square is one part table of OptoWaveform.
# For sine and ramp waveforms, see the corresponding tables
opto.OptoWaveform.Square.insert1(
    dict(waveform_name="square_10", on_proportion=0.10, off_proportion=0.90)
)


opto.OptoStimParams.insert1(
    dict(
        opto_params_id=1,
        waveform_name="square_10",
        wavelength=470,
        light_intensity=10.2,
        frequency=1,
        duration=241,
    )
)


# Next, we'll describe the session in which these parameters were used with `OptoProtocol`
#

opto.OptoProtocol.insert1(
    dict(
        subject="subject3",
        session_id="1",
        protocol_id="1",
        opto_params_id="1",
        implant_date="2022-04-01 12:13:14",
        implant_type="opto",
        target_region="dHP",
        target_hemisphere="left",
        device="OPTG_4",
    )
)


# We can describe the timing of these stimulations in `OptoEvent`.
#

opto.OptoEvent.insert(
    [
        dict(
            subject="subject3",
            session_id=1,
            protocol_id=1,
            stim_start_time=241,
            stim_end_time=482,
        ),
        dict(
            subject="subject3",
            session_id=1,
            protocol_id=1,
            stim_start_time=482,
            stim_end_time=723,
        ),
    ]
)


# To store more experimental timing information, see documentation for [Element Event](https://datajoint.com/docs/elements/element-event/).
#

# ## Automating inserts
#
# This workflow provides functions for ingesting this information from csv files in `ingest.py`.
#
# - `ingest_subjects`: subject.Subject
# - `ingest_sessions`: session.Session
# - `ingest_events`: Element Event schemas
# - `ingest_opto`: surgery and opto schemas
#
# For more information on each, see the docstring.
#

# +
from workflow_optogenetics.ingest import ingest_subjects

help(ingest_subjects)

# -

# By default, these functions pull from files in the `user_files` directory. We can run each of these in succession with the default parameters with `ingest_all`.
#

# +
from workflow_optogenetics.ingest import ingest_all

ingest_all()

# -

# ## Events
#
# The above `ingest_all()` also added behavioral events we can example in conjunction with optogenetic events. For convenience, these stimulation events are also reflected in the Block design of Element Event.
#

# +
from workflow_optogenetics.pipeline import event, trial

events_by_block = (
    trial.BlockTrial * trial.TrialEvent * trial.Block.Attribute
    & "attribute_name='stimulation'"
)
events_by_block
# -

# We can readily compare the count of events or event types across 'on' and 'off' stimulation conditions.

events_by_block & "attribute_value='on'"

events_by_block & "attribute_value='off'"

# ## Next Steps
#
# Interested in using Element Optogenetics for your own project? Reach out to the DataJoint team via [email](mailto:support@datajoint.com) or [Slack](https://datajoint.slack.com).
#
