import logging
import os
import sys
from contextlib import nullcontext
from pathlib import Path

import datajoint as dj
import pytest
from element_interface.utils import ingest_csv_to_table

from workflow_optogenetics.ingest import (
    ingest_all,
    ingest_events,
    ingest_opto,
    ingest_sessions,
    ingest_subjects,
)
from workflow_optogenetics.paths import get_opto_root_data_dir

__all__ = [
    "ingest_all",
    "ingest_events",
    "ingest_opto",
    "ingest_subjects",
    "ingest_sessions",
    "get_opto_root_data_dir",
]

# ---------------------- CONSTANTS ---------------------

logger = logging.getLogger("datajoint")


def pytest_addoption(parser):
    """
    Permit constants when calling pytest at commandline e.g., pytest --dj-verbose False

    Parameters
    ----------
    --dj-verbose (bool):  Default True. Pass print statements from Elements.
    --dj-teardown (bool): Default True. Delete pipeline on close.
    --dj-datadir (str):  Default ./tests/user_data. Relative path of test CSV data.
    """
    parser.addoption(
        "--dj-verbose",
        action="store",
        default="True",
        help="Verbose for dj items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--dj-teardown",
        action="store",
        default="True",
        help="Verbose for dj items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--dj-datadir",
        action="store",
        default="./tests/user_data",
        help="Relative path for saving tests data",
    )


@pytest.fixture(scope="session")
def setup(request):
    """Take passed commandline variables, set as global"""
    global verbose, _tear_down, test_user_data_dir, verbose_context

    verbose = str_to_bool(request.config.getoption("--dj-verbose"))
    _tear_down = str_to_bool(request.config.getoption("--dj-teardown"))
    test_user_data_dir = Path(request.config.getoption("--dj-datadir"))
    test_user_data_dir.mkdir(exist_ok=True)

    verbose_context = nullcontext() if verbose else QuietStdOut()

    yield verbose_context, verbose


# ------------------ GENERAL FUCNTION ------------------


def str_to_bool(value) -> bool:
    """Return whether the provided string represents true. Otherwise false.

    Args:
        value (any): Any input

    Returns:
        bool (bool): True if value in ("y", "yes", "t", "true", "on", "1")
    """
    # Due to distutils equivalent depreciation in 3.10
    # Adopted from github.com/PostHog/posthog/blob/master/posthog/utils.py
    if not value:
        return False
    return str(value).lower() in ("y", "yes", "t", "true", "on", "1")


def write_csv(path, content):
    """General function for writing strings to lines in CSV

    Args:
    path: pathlib PosixPath
    content: list of strings, each as row of CSV
    """
    with open(path, "w") as f:
        for line in content:
            f.write(line + "\n")


class QuietStdOut:
    """If verbose set to false, used to quiet tear_down table.delete prints"""

    def __enter__(self):
        logger.setLevel("WARNING")
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.setLevel("INFO")
        sys.stdout.close()
        sys.stdout = self._original_stdout


# ------------------- FIXTURES -------------------


@pytest.fixture(autouse=True, scope="session")
def dj_config():
    """If dj_local_config exists, load"""
    if Path("./dj_local_conf.json").exists():
        dj.config.load("./dj_local_conf.json")

    dj.config.update(
        {
            "safemode": False,
            "database.host": os.environ.get("DJ_HOST") or dj.config["database.host"],
            "database.password": os.environ.get("DJ_PASS")
            or dj.config["database.password"],
            "database.user": os.environ.get("DJ_USER") or dj.config["database.user"],
            "custom": {
                "database.prefix": os.environ.get("DATABASE_PREFIX")
                or dj.config["custom"]["database.prefix"],
                "dlc_root_data_dir": os.environ.get("DLC_ROOT_DATA_DIR")
                or dj.config["custom"]["dlc_root_data_dir"],
            },
        }
    )

    return


@pytest.fixture(scope="session")
def pipeline(setup):
    """Loads workflow_optogenetics.pipeline lab, session, subject, dlc"""
    with verbose_context:
        from workflow_optogenetics import pipeline

    yield {
        "lab": pipeline.lab,
        "subject": pipeline.subject,
        "surgery": pipeline.surgery,
        "session": pipeline.session,
        "opto": pipeline.opto,
        "Device": pipeline.Device,
    }
    if _tear_down:
        with verbose_context:
            pipeline.opto.OptoWaveform.delete()
            pipeline.surgery.BrainRegion.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.User.delete()


@pytest.fixture(scope="session")
def ingest_csvs(setup, pipeline):
    """For each input, generates csv in test_user_data_dir and ingests in schema"""
    # CSV as list of 3: filename, relevant tables, content
    all_csvs = {
        "subjects.csv": {
            "tables": [pipeline["subject"].Subject()],
            "content": [
                "subject,sex,subject_birth_date,subject_description",
                "subject3,F,2022-03-03,Optogenetic pilot subject",
            ],
        },
        "sessions.csv": {
            "tables": [pipeline["session"].Session()],
            "content": [
                "subject,session_dir,session_id,session_datetime",
                "subject3,subject3/opto_session1/,1,2022-04-04 12:13:14",
            ],
        },
        "opto_waveforms.csv": {
            "tables": [
                pipeline["opto"].OptoWaveform(),
                pipeline["opto"].OptoWaveform.Square(),
                pipeline["opto"].OptoStimParams(),
            ],
            "content": [
                "waveform_type,waveform_name,waveform_description,on_proportion,"
                + "off_proportion,opto_params_id,wavelength,light_intensity,frequency,"
                + "duration",
                "square,square_10,Square waveform with 10-90 on-off cycle,.10,"
                + ".90,1,470,10.2,1,241",
            ],
        },
        "opto_surgeries.csv": {
            "tables": [
                pipeline["surgery"].CoordinateReference(),
                pipeline["surgery"].BrainRegion(),
                pipeline["lab"].User(),
                pipeline["surgery"].Implantation(),
                pipeline["surgery"].Implantation.Coordinate(),
            ],
            "content": [
                "subject,implant_date,reference,region_acronym,region_name,hemisphere,"
                + "implant_type,ap,ap_ref,ml,ml_ref,dv,dv_ref,theta,phi,user,surgeon,"
                + "target_region,target_hemisphere",
                "subject3,2022-04-01 12:13:14,bregma,dHP,Dorsal Hippocampus,left,"
                + "opto,-7.9,bregma,-1.8,bregma,5,skull_surface,11.5,0,user1,user1,"
                + "dHP,left",
            ],
        },
        "opto_sessions.csv": {
            "tables": [
                pipeline["opto"].OptoProtocol(),
            ],
            "content": [
                "subject,session_id,protocol_id,opto_params_id,implant_date,"
                + "implant_type,target_region,target_hemisphere",
                "subject3,1,1,1,2022-04-01 12:13:14,opto,dHP,left",
            ],
        },
        "opto_events.csv": {
            "tables": [
                pipeline["opto"].OptoEvent(),
            ],
            "content": [
                "subject,session_id,protocol_id,stim_start_time,stim_end_time",
                "subject3,1,1,241,482",
                "subject3,1,1,482,723",
            ],
        },
    }
    # If data in last table, presume didn't tear down last time, skip insert
    if len(pipeline["opto"].OptoEvent()) == 0:
        for csv_filename, csv_dict in all_csvs.items():
            csv_path = test_user_data_dir / csv_filename  # add prefix for rel path
            write_csv(csv_path, csv_dict["content"])  # write content at rel path
            # repeat csv path n times as list to match n tables
            csv_path_as_list = [str(csv_path)] * len(csv_dict["tables"])
            ingest_csv_to_table(  # insert csv content into each of n tables
                csv_path_as_list,
                csv_dict["tables"],
                skip_duplicates=True,
                verbose=verbose,
            )

    yield

    if _tear_down:
        with verbose_context:
            for csv_info in all_csvs:
                csv_path = test_user_data_dir / csv_info[1]
                csv_path.unlink()
