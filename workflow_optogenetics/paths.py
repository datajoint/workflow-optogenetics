import pathlib

import datajoint as dj


def get_opto_root_data_dir():
    data_dir = dj.config.get("custom", {}).get("opto_root_data_dir", None)
    return pathlib.Path(data_dir) if data_dir else None
