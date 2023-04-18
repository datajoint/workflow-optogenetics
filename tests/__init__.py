"""
run all: python -m pytest tests/
run one: python -m pytest --pdb tests/module_name.py -k function_name
"""

import logging
import os
import sys
from contextlib import nullcontext
from pathlib import Path

import datajoint as dj
import pytest

# Constants ----------------------------------------------------------------------------

logger = logging.getLogger("datajoint")

_tear_down = True
verbose = True

# Functions ----------------------------------------------------------------------------


class QuietStdOut:
    """If verbose set to false, used to quiet table deletion print statements"""

    def __enter__(self):
        logger.setLevel("WARNING")
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.setLevel("INFO")
        sys.stdout.close()
        sys.stdout = self._original_stdout

verbose_context = nullcontext() if verbose else QuietStdOut()

# Fixtures -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def pipeline():
    """Loads lab, subject, session, optogenetics, Device"""
    with verbose_context:
        from workflow_optogenetics import pipeline

    yield {
        "lab": pipeline.lab,
        "subject": pipeline.subject,
        "surgery": pipeline.surgery,
        "session": pipeline.session,
        "optogenetics": pipeline.optogenetics,
        "Device": pipeline.Device,
    }
    if _tear_down:
        with verbose_context:
            pipeline.optogenetics.OptoWaveform.delete()
            pipeline.surgery.BrainRegion.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.User.delete()
