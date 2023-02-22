def test_upstream_pipeline(pipeline):
    session = pipeline["session"]
    surgery = pipeline["surgery"]
    subject = pipeline["subject"]

    # test connection Subject->Session
    assert subject.Subject.full_table_name == session.Session.parents()[0]
    assert subject.Subject.full_table_name in surgery.Implantation.parents()


def test_opto_pipeline(pipeline):
    session = pipeline["session"]
    surgery = pipeline["surgery"]
    opto = pipeline["opto"]
    Device = pipeline["Device"]

    # test connection opto.OptoProtocol -> schema children
    opto_parent_links = opto.OptoProtocol.parents()
    opto_parent_list = [
        session.Session,
        opto.OptoStimParams,
        surgery.Implantation,
        Device,
    ]
    for parent in opto_parent_list:
        assert (
            parent.full_table_name in opto_parent_links
        ), f"opto.OptoProtocol.parents() did not include {parent.full_table_name}"
