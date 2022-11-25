FROM --platform=linux/amd64 tiryoh/ubuntu-desktop-lxde-vnc:jammy

RUN apt update && apt install -y python3-pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV USER ubuntu
