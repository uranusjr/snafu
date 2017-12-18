# Dockerfile used to test the installer in a clean environment.
# TODO: Write tests to run inside the container.

FROM microsoft/windowsservercore

ARG SNAFU_SETUP_EXE

COPY $SNAFU_SETUP_EXE snafu-setup.exe
RUN snafu-setup.exe /S

RUN snafu install 3.6
RUN snafu use 3.6

RUN snafu list
RUN snafu list --all

RUN pip3.6 install django

RUN where django-admin

RUN snafu use --reset
RUN snafu list --all

# This doesn't work because (I think) the installer needs user interaction.
# We need to implement a --quiet option in the future.
# RUN snafu uninstall 3.6
