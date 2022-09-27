# run tests: pytest -sv --cov-report term-missing --cov=workflow_optogenetics -p no:warnings

import os
import pytest
import pathlib
import numpy as np
import pandas as pd
import datajoint as dj
from workflow_optogenetics.paths import get_opto_root_data_dir

# ------------------- SOME CONSTANTS -------------------

_tear_down = False

test_user_data_dir = pathlib.Path('./tests/user_data')
test_user_data_dir.mkdir(exist_ok=True)

sessions_dirs = ['subject0/session1',
                 'subject1/20200609_170519',
                 'subject1/20200609_171646',
                 'subject2/20200420_1843959',
                 'subject3/210107_run00_orientation_8dir']

is_multi_scan_processing = False

# ------------------- FIXTURES -------------------


@pytest.fixture(autouse=True)
def dj_config():
    if pathlib.Path('./dj_local_conf.json').exists():
        dj.config.load('./dj_local_conf.json')
    dj.config['safemode'] = False
    dj.config['custom'] = {
        'database.prefix': (os.environ.get('DATABASE_PREFIX')
                            or dj.config['custom']['database.prefix']),
        'opto_root_data_dir': (os.environ.get('OPTO_ROOT_DATA_DIR')
                                  or dj.config['custom']['opto_root_data_dir'])
    }
    return


@pytest.fixture(autouse=True)
def test_data(dj_config):
    test_data_dir = pathlib.Path(dj.config['custom']['opto_root_data_dir'])

    test_data_exists = np.all([(test_data_dir / p).exists() for p in sessions_dirs])

    if not test_data_exists:
        try:
            dj.config['custom'].update({
                'djarchive.client.endpoint': os.environ['DJARCHIVE_CLIENT_ENDPOINT'],
                'djarchive.client.bucket': os.environ['DJARCHIVE_CLIENT_BUCKET'],
                'djarchive.client.access_key': os.environ['DJARCHIVE_CLIENT_ACCESSKEY'],
                'djarchive.client.secret_key': os.environ['DJARCHIVE_CLIENT_SECRETKEY']
            })
        except KeyError as e:
            raise FileNotFoundError(
                f'Test data not available at {test_data_dir}.'
                f'\nAttempting to download from DJArchive,'
                f' but no credentials found in environment variables.'
                f'\nError: {str(e)}')

        import djarchive_client
        from workflow_optogenetics import version

        client = djarchive_client.client()
        workflow_version = version.__version__

        client.download('workflow-calcium-ephys-test-set',
                        workflow_version.replace('.', '_'),
                        str(test_data_dir), create_target=False)
    return


@pytest.fixture
def pipeline():
    from workflow_optogenetics import pipeline

    global is_multi_scan_processing
    is_multi_scan_processing = 'processing_task_id' in pipeline.imaging.ProcessingTask.heading.names

    yield {'subject': pipeline.subject,
           'lab': pipeline.lab,
           'imaging': pipeline.imaging,
           'scan': pipeline.scan,
           'session': pipeline.session,
           'Equipment': pipeline.Equipment,
           'get_opto_root_data_dir': pipeline.get_opto_root_data_dir}

    if _tear_down:
        pipeline.subject.Subject.delete()


@pytest.fixture
def subjects_csv():
    """ Create a 'subjects.csv' file"""
    input_subjects = pd.DataFrame(columns=['subject', 'sex',
                                           'subject_birth_date',
                                           'subject_description'])
    input_subjects.subject = ['subject0', 'subject1', 'subject2', 'subject3']
    input_subjects.sex = ['M', 'F', 'M', 'F']
    input_subjects.subject_birth_date = [
        '2020-01-01 00:00:01', '2020-01-01 00:00:01',
        '2020-01-01 00:00:01', '2020-01-01 00:00:01']
    input_subjects.subject_description = ['mika_animal', '91760', '90853', 'sbx-JC015']
    input_subjects = input_subjects.set_index('subject')

    subjects_csv_path = pathlib.Path('./tests/user_data/subjects.csv')
    input_subjects.to_csv(subjects_csv_path)  # write csv file

    yield input_subjects, subjects_csv_path

    if _tear_down:
        subjects_csv_path.unlink()  # delete csv file after use


@pytest.fixture
def ingest_subjects(pipeline, subjects_csv):
    from workflow_optogenetics.ingest import ingest_subjects
    _, subjects_csv_path = subjects_csv
    ingest_subjects(subjects_csv_path)
    return


@pytest.fixture
def sessions_csv(test_data):
    """ Create a 'sessions.csv' file"""
    root_dir = pathlib.Path(get_opto_root_data_dir())

    input_sessions = pd.DataFrame(columns=['subject', 'session_dir'])
    input_sessions.subject = ['subject0',
                              'subject1',
                              'subject1',
                              'subject2',
                              'subject3']
    input_sessions.session_dir = [(root_dir / sess_dir).as_posix()
                                  for sess_dir in sessions_dirs]
    input_sessions = input_sessions.set_index('subject')

    sessions_csv_path = pathlib.Path('./tests/user_data/sessions.csv')
    input_sessions.to_csv(sessions_csv_path)  # write csv file

    yield input_sessions, sessions_csv_path

    if _tear_down:
        sessions_csv_path.unlink()  # delete csv file after use


@pytest.fixture
def ingest_sessions(ingest_subjects, sessions_csv):
    from workflow_optogenetics.ingest import ingest_sessions
    _, sessions_csv_path = sessions_csv
    ingest_sessions(sessions_csv_path)
    return


@pytest.fixture
def testdata_paths():
    return {
        'scanimage_2d': 'subject1/20200609_171646',
        'scanimage_3d': 'subject2/20200420_1843959',
        'scanimage_multiroi': 'subject0/session1',
        'scanbox_3d': 'subject3/210107_run00_orientation_8dir',
        'suite2p_2d': 'subject1/20200609_171646/suite2p',
        'suite2p_3d_a': 'subject2/20200420_1843959/suite2p',
        'suite2p_3d_b': 'subject3/210107_run00_orientation_8dir/suite2p',
        'caiman_2d': 'subject1/20200609_170519/caiman'
    }


@pytest.fixture
def processing(processing_tasks, pipeline):
    imaging = pipeline['imaging']

    errors = imaging.Processing.populate(suppress_errors=True)

    if errors:
        print(f'Populate ERROR: {len(errors)} errors in "imaging.Processing.populate()" - {errors[0][-1]}')

    yield

    if _tear_down:
        imaging.Processing.delete()

