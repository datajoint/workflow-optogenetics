__all__ = ["pipeline"]


def test_upstream_pipeline(pipeline):
    session = pipeline["session"]
    subject = pipeline["subject"]

    # test connection Subject->Session
    assert subject.Subject.full_table_name == session.Session.parents()[0]


def test_opto_pipeline(pipeline):
    opto = pipeline["opto"]

    # test connection opto.VideoRec -> schema children
    opto_children_links = opto.TABLE.children()
    opto_children_list = [
        opto.TABLE.File,
    ]
    for child in opto_children_list:
        assert (
            child.full_table_name in opto_children_links
        ), f"opto.TABLE.children() did not include {child.full_table_name}"
