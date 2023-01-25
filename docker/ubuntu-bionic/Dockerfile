#FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
FROM nvidia/cudagl:9.2-base-ubuntu18.04

ENV DEBIAN_FRONTEND noninteractive

# install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -q -y \
    dirmngr \
    gnupg2 \
    git \ 
	libglu1-mesa-dev \
	pulseaudio \
	python3 \
	python3-pip \
	sudo \
	sudo \
	wget \ 
	x11-xserver-utils \
	xdg-user-dirs \
	unzip \
    && rm -rf /var/lib/apt/lists/*

# create user
RUN bash -c "useradd -ms /bin/bash nvagent"
RUN usermod -aG sudo nvagent
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER nvagent
WORKDIR /home/nvagent
ENV USER nvagent

RUN sudo chown -R $USER /home/$USER

RUN git clone https://github.com/microsoft/AirSim-NeurIPS2019-Drone-Racing && \
	cd AirSim-NeurIPS2019-Drone-Racing && \
	bash download_training_binaries.sh && \
	bash download_qualification_binaries.sh && \
	mv AirSim_Training/ ../ && \
	mv AirSim_Qualification/ ../ && \
	cd ../

RUN DEBIAN_FRONTEND=noninteractive sudo apt-get update && sudo apt-get install -y git curl software-properties-common apt-utils python python-pip wget sudo unzip
RUN DEBIAN_FRONTEND=noninteractive sudo apt-get install -y mesa-utils

RUN bash -c 'git config --global user.name "drone_rescue_docker_build"'
RUN python -m pip install msgpack-rpc-python numpy pillow airsim==1.2.4 --user

RUN wget https://github.com/microsoft/AirSim/releases/download/v1.2.0Linux/Blocks.zip
RUN unzip Blocks.zip

COPY runtime_test.py runtime_test.py
COPY runtime_test.sh runtime_test.sh
RUN git clone https://github.com/microsoft/DroneRescue
ENTRYPOINT /home/nvagent/runtime_test.sh
