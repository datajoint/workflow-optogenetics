import datajoint as dj
from element_lab import lab
from element_animal import subject
from element_session import session_with_datetime as session
from element_event import trial, event
from element_optogenetics import optogenetics as opto
from element_lab.lab import Source, Lab, Protocol, User, Location, Project
from element_animal.subject import Subject
from .paths import get_opto_root_data_dir

if "custom" not in dj.config:
    dj.config["custom"] = {}

db_prefix = dj.config["custom"].get("database.prefix", "")

__all__ = [
    "subject",
    "lab",
    "session",
    "Equipment",
    "trial",
    "event",
    "scan",
    "opto",
    "Subject",
    "Source",
    "Lab",
    "Protocol",
    "User",
    "Project",
    "Session",
    "Location",
    "get_opto_root_data_dir",
]


# Activate "lab", "subject", "session" schema -----------------------

lab.activate(db_prefix + "lab")

subject.activate(db_prefix + "subject", linking_module=__name__)

Session = session.Session
Experimenter = lab.User
session.activate(db_prefix + "session", linking_module=__name__)


# Activate "event" and "trial" schema ---------------------------------

trial.activate(db_prefix + "trial", db_prefix + "event", linking_module=__name__)


# Declare table Equipment for use in element_optogenetics --------------


@lab.schema
class Equipment(dj.Manual):
    definition = """
    scanner: varchar(32)
    """


@lab.schema
class SkullReference(dj.Lookup):
    definition = """
    skull_reference   : varchar(60)
    """
    contents = zip(["Bregma", "Lambda"])


# ------------- Activate "opto" schema -------------

opto.activate(db_prefix + "opto", linking_module=__name__)
