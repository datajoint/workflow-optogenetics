"""Tests ingestion into schema tables: Lab, Subject, Session
    1. Assert length of populating data conftest
    2. Assert exact matches of inserted data fore key tables
"""


def test_ingest(pipeline, ingest_csvs):
    """Check successful ingestion of csv data"""
    import datetime

    subject = pipeline["subject"]
    session = pipeline["session"]
    opto = pipeline["opto"]

    table_lengths = [
        (subject.Subject(), 1, "subject6"),
        (session.Session(), 2, datetime.datetime(2021, 6, 1, 13, 33, 33)),
        (opto.TABLE(), 1, "from_top_tracking"),
        (opto.TABLE(), 3, 0),
        (
            opto.TABLE.File(),
            10,
            "path/file.ext",
        ),
    ]

    for t in table_lengths:
        assert len(t[0]) == t[1], f"Check length of {t[0].full_table_name}"
        assert t[2] in t[0].fetch()[0], f"Check contents of {t[0].full_table_name}"
