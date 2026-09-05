## Build instructions for Linux using Docker

### Prepare folder

Choose a folder for the future build, for example **/home/user/TBuild**. It will be named ***BuildPath*** in the rest of this document. All commands will be launched from Terminal.

### Clone source code and prepare libraries

Install [poetry](https://python-poetry.org), [docker](https://www.docker.com/) and [docker-buildx](https://docs.docker.com/reference/cli/docker/buildx/), go to ***BuildPath*** and run

    git clone --recursive https://github.com/AyuGram/AyuGramDesktop.git tdesktop
    ./tdesktop/Telegram/build/prepare/linux.sh

### Building the project

Register application credentials through [Telegram](https://core.telegram.org/api/obtaining_api_id)
and export `TDESKTOP_API_ID` and `TDESKTOP_API_HASH` in the build shell.
For preview binaries, also pass `-D DESKTOP_APP_DISABLE_AUTOUPDATE=ON` until
the distribution meets the [release requirements](releasing.md).

Go to ***BuildPath*/tdesktop** and run

    docker run --rm -it \
        -u $(id -u) \
        -v "$PWD:/usr/src/tdesktop" \
        ghcr.io/telegramdesktop/tdesktop/centos_env:latest \
        /usr/src/tdesktop/Telegram/build/docker/centos_env/build.sh \
        -D "TDESKTOP_API_ID=$TDESKTOP_API_ID" \
        -D "TDESKTOP_API_HASH=$TDESKTOP_API_HASH"

Or, to create a debug build, run

    docker run --rm -it \
        -u $(id -u) \
        -v "$PWD:/usr/src/tdesktop" \
        -e CONFIG=Debug \
        ghcr.io/telegramdesktop/tdesktop/centos_env:latest \
        /usr/src/tdesktop/Telegram/build/docker/centos_env/build.sh \
        -D "TDESKTOP_API_ID=$TDESKTOP_API_ID" \
        -D "TDESKTOP_API_HASH=$TDESKTOP_API_HASH"

The built files will be in the `out` directory.

You can use `strip` command to reduce binary size.

### Visual Studio Code integration

Ensure you've followed the instruction up to the [**Clone source code and prepare libraries**](#clone-source-code-and-prepare-libraries) step at least.

Open the repository in Visual Studio Code, install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension and add the following to `.vscode/settings.json` (using [your **api_id** and **api_hash**](#obtain-your-api-credentials)):

    {
        "cmake.configureSettings": {
            "TDESKTOP_API_ID": "YOUR_API_ID",
            "TDESKTOP_API_HASH": "YOUR_API_HASH"
        }
    }

After that, choose **Reopen in Container** via the menu triggered by the green button in bottom left corner and you're done.

![Quick actions Status bar item](https://code.visualstudio.com/assets/docs/devcontainers/containers/remote-dev-status-bar.png)
