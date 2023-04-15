from element_animal import subject, surgery
from element_animal.subject import Subject  # Dependency for session schema
from element_animal.surgery import Implantation  # Dependency for optogenetics schema
from element_lab import lab
from element_lab.lab import User as Experimenter  # Alias for session schema
from element_lab.lab import Lab, Project, Protocol, Source
from element_optogenetics import optogenetics
from element_session import session_with_id as session
from element_session.session_with_id import Session

from . import db_prefix
from .reference import Device

__all__ = [
    "lab",
    "optogenetics",
    "session",
    "subject",
    "surgery",
    "Device",
    "Implantation",
    "Lab",
    "Project",
    "Protocol",
    "Session",
    "Source",
    "Subject",
    "User",
]


# Activate "lab", "subject", "surgery", "session" schemas -------

lab.activate(db_prefix + "lab")
subject.activate(db_prefix + "subject", linking_module=__name__)
surgery.activate(db_prefix + "surgery", linking_module=__name__)
session.activate(db_prefix + "session", linking_module=__name__)

# Activate "optogenetics" schema -------------

optogenetics.activate(db_prefix + "optogenetics", linking_module=__name__)
