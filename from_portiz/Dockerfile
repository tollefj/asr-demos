FROM nvidia/cuda:11.4.3-cudnn8-devel-ubuntu20.04

RUN apt update
RUN apt install -y git git-lfs python3-pip
RUN git lfs install

# Specific for running with username in Loke, repos and other shall be placed in your home
ARG UID
ARG username
RUN test -n "$UID" || (echo "UID not set, use e.g. --build-arg UID=\$(id -u)" && false)
RUN mkdir /home/$username && chown -R $UID:$UID /home/$username

# These packages are manually selected from the repo requirements
RUN pip install pyannote.audio pydub rich tqdm transformers librosa numba numpy webrtcvad
#RUN pip install numpy pandas matplotlib scikit-learn torch==1.11.0 pytorch_lightning==1.9 wandb seaborn optuna accelerate mycolorpy

# Define the default User all commands will be run as within any
# container created from your Image. It can be either a UID or username
RUN adduser --disabled-password --gecos "" --uid $UID $username

# Switch to user
USER $username