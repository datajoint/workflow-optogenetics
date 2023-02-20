#!/usr/bin/env python
from element_interface.utils import ingest_csv_to_table

from .pipeline import event, lab, opto, session, subject, surgery, trial

___all__ = [
    "subject",
    "surgery",
    "session",
    "trial",
    "event",
    "opto",
    "ingest_csv_to_table",
    "ingest_subjects",
    "ingest_sessions",
    "ingest_events",
    "ingest_opto",
    "ingest_all",
]


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

    csvs = [session_csv_path]
    tables = [session.Session()]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


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
    units). Events are optionally-instantaneous occurrences within trial. This ingestion
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
    opto_surgery_csv_path: str = "./user_data/opto_surgeries.csv",
    opto_session_csv_path: str = "./user_data/opto_sessions.csv",
    opto_events_csv_path: str = "./user_data/opto_events.csv",
    waveform_csv_path: str = "./user_data/opto_waveforms.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest optogenetic stimulation and protocol information.

    Args:
        opto_surgery_csv_path (str, optional): Relative path to implantation info CSV.
            Defaults to "./user_data/opto_surgeries.csv".
        opto_session_csv_path (str, optional): Relative path to CSV with opto session
            information. Defaults to "./user_data/opto_sessions.csv".
        opto_events_csv_path (str, optional): Relative path to opto events CSV.
            Defaults to "./user_data/opto_events.csv".
        waveform_csv_path (str, optional): Relative path to waveform info CSV.
            Defaults to "./user_data/opto_waveforms.csv".
        skip_duplicates (bool, optional): Skips duplicates, see DataJoint insert.
            Defaults to True.
        verbose (bool, optional): Provides insertion info to StdOut. Defaults to True.
    """
    csvs = [
        waveform_csv_path,  # 1
        waveform_csv_path,  # 2
        waveform_csv_path,  # 3
        opto_surgery_csv_path,  # 4
        opto_surgery_csv_path,  # 5
        opto_surgery_csv_path,  # 6
        opto_surgery_csv_path,  # 7
        opto_surgery_csv_path,  # 8
        opto_session_csv_path,  # 9
        opto_events_csv_path,  # 10
    ]
    tables = [
        opto.OptoWaveform(),  # 1
        opto.OptoWaveform.Square(),  # 2
        opto.OptoStimParams(),  # 3
        surgery.CoordinateReference(),  # 4
        surgery.BrainRegion(),  # 5
        lab.User(),  # 6
        surgery.Implantation(),  # 7
        surgery.Implantation.Coordinate(),  # 8
        opto.OptoProtocol(),  # 9
        opto.OptoEvent(),  # 10
    ]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


def ingest_all(skip_duplicates: bool = True, verbose: bool = True):
    """Run all available available ingestion functions"""
    ingest_subjects(skip_duplicates=skip_duplicates, verbose=verbose)
    ingest_sessions(skip_duplicates=skip_duplicates, verbose=verbose)
    ingest_events(skip_duplicates=skip_duplicates, verbose=verbose)
    ingest_opto(skip_duplicates=skip_duplicates, verbose=verbose)


if __name__ == "__main__":
    ingest_all()
