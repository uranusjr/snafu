# Dockerfile used to test the installer in a clean environment.
# TODO: Write tests to run inside the container.

FROM microsoft/windowsservercore

ARG SNAFU_SETUP_EXE

COPY $SNAFU_SETUP_EXE snafu-setup.exe
RUN snafu-setup.exe /S

RUN snafu install 3.6
RUN python3.6 --version

RUN pip3.6 install python-dotenv
RUN where dotenv

RUN snafu list
RUN snafu list --all

RUN python3 --version

RUN pip3 install pytest
RUN where pytest

RUN snafu use 3.6
RUN snafu use --reset
RUN snafu list --all

RUN snafu uninstall 3.6
