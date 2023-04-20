from . import pipeline


def test_upstream_pipeline(pipeline):
    session = pipeline["session"]
    surgery = pipeline["surgery"]
    subject = pipeline["subject"]

    # Test connection from Subject to parent tables
    assert subject.Subject.full_table_name in session.Session.parents()
    assert subject.Subject.full_table_name in surgery.Implantation.parents()


def test_optogenetics_pipeline(pipeline):
    session = pipeline["session"]
    surgery = pipeline["surgery"]
    optogenetics = pipeline["optogenetics"]
    Device = pipeline["Device"]

    # Test connection from optogenetics.OptoProtocol to parent tables
    assert session.Session.full_table_name in optogenetics.OptoProtocol.parents()
    assert (
        optogenetics.OptoStimParams.full_table_name
        in optogenetics.OptoProtocol.parents()
    )
    assert surgery.Implantation.full_table_name in optogenetics.OptoProtocol.parents()
    assert Device.full_table_name in optogenetics.OptoProtocol.parents()

    assert "stim_start_time" in optogenetics.OptoEvent.heading.attributes
