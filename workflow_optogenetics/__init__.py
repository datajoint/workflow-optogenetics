import os
import datajoint as dj


if 'custom' not in dj.config:
    dj.config['custom'] = {}

dj.config['custom']['database.prefix'] = os.getenv(
    'DATABASE_PREFIX',
    dj.config['custom'].get('database.prefix', ''))

db_prefix = dj.config["custom"].get("database.prefix", "")
