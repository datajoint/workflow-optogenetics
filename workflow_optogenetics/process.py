from workflow_optogenetics.pipeline import opto
import warnings

warnings.filterwarnings("ignore")


def run(display_progress=True):

    populate_settings = {
        "display_progress": display_progress,
        "reserve_jobs": False,
        "suppress_errors": False,
    }

    print("\n---- Populate imported and computed tables ----")

    opto.TABLE.populate(**populate_settings)

    print("\n---- Successfully completed workflow_optogenetics/process.py ----")


if __name__ == "__main__":
    run()
