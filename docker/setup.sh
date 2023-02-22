#! /bin/bash
export $(grep -v '^#' /main/.env | xargs)

echo "INSTALL OPTION:" $INSTALL_OPTION
cd /main/
# all local installs, mapped from host
if [ "$INSTALL_OPTION" == "local-all" ]; then
    for f in lab animal session event optogenetics; do
        pip install -e ./element-${f}
    done
    pip install -e ./workflow-optogenetics
# all except workflow pip installed
else
    pip install git+https://github.com/${GITHUB_USERNAME}/element-lab.git
    pip install git+https://github.com/${GITHUB_USERNAME}/element-animal.git
    pip install git+https://github.com/${GITHUB_USERNAME}/element-session.git
    pip install git+https://github.com/${GITHUB_USERNAME}/element-event.git
    # only optogenetics items from local install
    if [ "$INSTALL_OPTION" == "local-only" ]; then
        pip install -e ./element-optogenetics
        pip install -e ./workflow-optogenetics
    # all from github
    elif [ "$INSTALL_OPTION" == "git" ]; then
        pip install git+https://github.com/${GITHUB_USERNAME}/element-optogenetics.git
        pip install git+https://github.com/${GITHUB_USERNAME}/workflow-optogenetics.git
    fi
fi

# If test cmd contains pytest, install
if [[ "$TEST_CMD" == *pytest* ]]; then
    pip install pytest
    pip install pytest-cov
fi
