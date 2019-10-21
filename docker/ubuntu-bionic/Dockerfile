FROM ubuntu:bionic
ENV DEBIAN_FRONTEND noninteractive

# install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -q -y \
    dirmngr \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*


RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y git curl software-properties-common apt-utils python python-pip
RUN bash -c 'git config --global user.name "pabloinigoblasco"'

RUN python -m pip install msgpack-rpc-python numpy pillow airsim==1.2.4 --user

#COPY AirSim.tar.gz /root/AirSim.tar.gz
#RUN cd /root; tar xfvz AirSim.tar.gz 

#RUN bash -c "cd UnrealEngine; ./Setup.sh; ./GenerateProjectFiles.sh; make"
RUN git clone https://github.com/microsoft/DroneRescue

