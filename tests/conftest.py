import os
import sys
import pytest
import logging
from pathlib import Path
from contextlib import nullcontext
from element_optogenetics.optogenetics import str_to_bool
import datajoint as dj
from element_interface.utils import find_full_path
from workflow_optogenetics.paths import get_opto_root_data_dir
from workflow_optogenetics.ingest import (
    ingest_subjects,
    ingest_sessions,
    ingest_train_params,
    ingest_train_vids,
    ingest_model_vids,
    ingest_model,
)

__all__ = [
    "ingest_subjects",
    "ingest_sessions",
    "ingest_train_params",
    "ingest_train_vids",
    "ingest_model_vids",
]

# ---------------------- CONSTANTS ---------------------

test_data_project = "from_top_tracking"
inference_vid = f"{test_data_project}/videos/test.mp4"
inf_vid_short = f"{test_data_project}/videos/test-2s.mp4"
model_name = "FromTop-latest"


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
        os.environ["DJ_LOG_LEVEL"] = "WARNING"
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ["DJ_LOG_LEVEL"] = "INFO"
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
        "opto": pipeline.opto,
        "subject": pipeline.subject,
        "session": pipeline.session,
        "lab": pipeline.lab,
        "Device": pipeline.Device,
    }
    if _tear_down:
        with verbose_context:
            pipeline.opto.OptoSession.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.Lab.delete()
            pipeline.train.TrainingParamSet.delete()


@pytest.fixture(scope="session")
def ingest_csvs(setup, test_data, pipeline):
    """For each input, generates csv in test_user_data_dir and ingests in schema"""
    # CSV as list of 3: relevant insert func, filename, content
    all_csvs = [
        [  # 0
            ingest_subjects,
            "subjects.csv",
            [
                "subject,sex,subject_birth_date,subject_description,"
                + "death_date,cull_method",
                "subject6,M,2020-01-01 00:00:01,manuel,2020-10-03 00:00:01,natural",
            ],
        ],
        [  # 1
            ingest_sessions,
            "sessions.csv",
            [
                "subject,session_datetime,session_dir,session_note",
                f"subject6,2021-06-01 13:33:33,{test_data_project}/,Model Training",
                f"subject6,2021-06-02 14:04:22,{test_data_project}/,Test Session",
            ],
        ],
    ]

    # If data in last table, presume didn't tear down last time, skip insert
    if len(pipeline["opto"].OptoSession()) == 0:
        for csv_info in all_csvs:
            csv_path = test_user_data_dir / csv_info[1]
            write_csv(csv_path, csv_info[2])
            csv_info[0](csv_path, skip_duplicates=True, verbose=verbose)

    yield

    if _tear_down:
        with verbose_context:
            for csv_info in all_csvs:
                csv_path = test_user_data_dir / csv_info[1]
                csv_path.unlink()


@pytest.fixture(scope="session")
def populate_settings():
    yield dict(display_progress=verbose, reserve_jobs=False, suppress_errors=False)


@pytest.fixture()
def feature(pipeline, populate_settings):
    """Other feature of pipeline"""
    yield pipeline["opto"].TABLE.populate(**populate_settings)
