from . import dj_config, pipeline


def test_generate_pipeline(pipeline):
    subject = pipeline['subject']
    opto = pipeline['opto']
    session = pipeline['session']
    Equipment = pipeline['Equipment']

    subject_tbl, *_ = session.Session.parents(as_objects=True)

    # test elements connection from lab, subject to Session
    assert subject_tbl.full_table_name == subject.Subject.full_table_name

    # test elements connection from Session to opto
    session_tbl, equipment_tbl, _ = opto.TABLE.parents(as_objects=True)
    assert session_tbl.full_table_name == session.Session.full_table_name
    assert equipment_tbl.full_table_name == Equipment.full_table_name
    assert 'mask_npix' in opto.TABLE.heading.secondary_attributes
