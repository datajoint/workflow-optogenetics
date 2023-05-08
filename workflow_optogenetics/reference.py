import datajoint as dj

from . import db_prefix

schema = dj.Schema(db_prefix + "reference")


@schema
class Device(dj.Lookup):
    """Table for managing lab devices.

    Attributes:
        device ( varchar(32) ): Device short name.
        modality ( varchar(64) ): Modality for which this device is used.
        description ( varchar(256), optional ): Description of device.
    """

    definition = """
    device             : varchar(32)
    ---
    modality           : varchar(64)
    description=''     : varchar(256)
    """
    contents = [
        ["OPTG_4", "Optogenetics", "Doric Pulse Sequence Generator"],
    ]
