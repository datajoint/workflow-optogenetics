"""Tests ingestion into schema tables: Lab, Subject, Session
    1. Assert length of populating data conftest
    2. Assert exact matches of inserted data fore key tables
"""


def test_ingest(pipeline, ingest_csvs):
    """Check successful ingestion of csv data"""
    import datetime

    subject = pipeline["subject"]
    session = pipeline["session"]
    surgery = pipeline["surgery"]
    opto = pipeline["opto"]

    table_lengths = [
        (subject.Subject(), 1, "subject3"),
        (session.Session(), 1, datetime.datetime(2022, 4, 4, 12, 13, 14)),
        (surgery.Implantation.Coordinate(), 1, 11.5),
        (opto.OptoStimParams(), 1, "square_10"),
        (opto.OptoEvent(), 2, 482),
    ]

    for t in table_lengths:
        assert len(t[0]) == t[1], f"Check length of {t[0].full_table_name}"
        assert t[2] in t[0].fetch()[0], f"Check contents of {t[0].full_table_name}"
