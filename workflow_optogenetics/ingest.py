import csv
import pathlib
from pathlib import Path
from datetime import datetime
from element_interface.utils import find_full_path, ingest_csv_to_table
from workflow_optogenetics.pipeline import (
    subject,
    scan,
    session,
    Device,
    trial,
    event,
    opto,
)


def ingest_subjects(
    subject_csv_path: str = "./user_data/subjects.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest subjects listed in the subject column of ./user_data/subjects.csv

    Args:
        subject_csv_path (str, optional): Relative path to subject csv.
            Defaults to "./user_data/subjects.csv".
        skip_duplicates (bool, optional): Skips duplicates, see DataJoint insert.
            Defaults to True.
        verbose (bool, optional): Provides insertion info to StdOut. Defaults to True.
    """
    csvs = [subject_csv_path]
    tables = [subject.Subject()]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


def ingest_sessions(
    session_csv_path: str = "./user_data/sessions.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest sessions from CSV. Defaults to ./user_data/subjects.csv

    Args:
        session_csv_path (str, optional): Relative path to sessions CSV.
            Defaults to "./user_data/sessions.csv".
        skip_duplicates (bool, optional): Skips duplicates, see DataJoint insert.
            Defaults to True.
        verbose (bool, optional): Provides insertion info to StdOut. Defaults to True.
    """
    pass


def ingest_events(
    recording_csv_path: str = "./user_data/behavior_recordings.csv",
    block_csv_path: str = "./user_data/blocks.csv",
    trial_csv_path: str = "./user_data/trials.csv",
    event_csv_path: str = "./user_data/events.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest trial structure: blocks, trials, events

    A recording is one or more blocks (i.e., phases of trials), with trials (repeated
    units). Events are optionally-instantaneous occurences within trial. This ingestion
    function is duplicated across multiple DataJoint workflow repositories.

    Args:
        recording_csv_path (str, optional): Relative path to recording CSV.
            Defaults to "./user_data/behavior_recordings.csv".
        block_csv_path (str, optional): Relative path to block CSV.
            Defaults to "./user_data/blocks.csv".
        trial_csv_path (str, optional): Relative path to trial CSV.
            Defaults to "./user_data/trials.csv".
        event_csv_path (str, optional): Relative path to event CSV.
            Defaults to "./user_data/events.csv".
        skip_duplicates (bool, optional): Skips duplicates, see DataJoint insert.
            Defaults to True.
        verbose (bool, optional): Provides insertion info to StdOut. Defaults to True.
    """
    csvs = [
        recording_csv_path,
        recording_csv_path,
        block_csv_path,
        block_csv_path,
        trial_csv_path,
        trial_csv_path,
        trial_csv_path,
        trial_csv_path,
        event_csv_path,
        event_csv_path,
        event_csv_path,
    ]
    tables = [
        event.BehaviorRecording(),
        event.BehaviorRecording.File(),
        trial.Block(),
        trial.Block.Attribute(),
        trial.TrialType(),
        trial.Trial(),
        trial.Trial.Attribute(),
        trial.BlockTrial(),
        event.EventType(),
        event.Event(),
        trial.TrialEvent(),
    ]

    # Allow direct insert required bc element-trial has Imported tables
    ingest_csv_to_table(
        csvs,
        tables,
        skip_duplicates=skip_duplicates,
        verbose=verbose,
        allow_direct_insert=True,
    )


def ingest_opto(
    waveform_csv_path: str = "./user_data/opto_waveform.csv",
    opto_session_csv_path: str = "./user_data/opto_session.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest optogenetic stimulation and protocol information.

    Args:
        waveform_csv_path (str, optional): Relative path to waveform info CSV.
            Defaults to "./user_data/opto_waveform.csv".
        opto_session_csv_path (str, optional): Relative path to CSV with opto protocol
            information, session and session brain location.
            Defaults to "./user_data/opto_session.csv".
        skip_duplicates (bool, optional): Skips duplicates, see DataJoint insert.
            Defaults to True.
        verbose (bool, optional): Provides insertion info to StdOut. Defaults to True.
    """
    csvs = [
        waveform_csv_path,
        waveform_csv_path,
        opto_session_csv_path,
        opto_session_csv_path,
        opto_session_csv_path,
    ]
    tables = [
        opto.Waveform(),
        opto.Waveform.Square(),
        opto.Protocol(),
        opto.SessionProtocol(),
        opto.SessionBrainLocation(),
    ]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


if __name__ == "__main__":
    ingest_subjects()
    ingest_sessions()
    ingest_events()
    ingest_opto()
