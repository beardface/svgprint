#################################################
# Dockerfile to build openlase / lasershark supporting ubuntu
#

FROM ubuntu

MAINTAINER Justin Hawkins

RUN apt-get update
RUN apt-get -y install git
RUN mkdir openlase

#install openlase
RUN apt-get -y install cmake gcc build-essential libjack-jackd2-dev python libqt4-dev libavcodec-dev
RUN apt-get -y install libswscale-dev freeglut3-dev libasound2-dev libncurses5-dev yasm python-dev
RUN apt-get -y install cython libxmu-dev libxi-dev

#install lasershark
RUN apt-get -y install libusb-1.0-0-dev jackd2 libjack-jackd2-dev gcc build-essential
RUN git clone https://github.com/macpod/lasershark_hostapp.git
WORKDIR /lasershark_hostapp
RUN make
RUN ls
RUN echo ATTRS{idVendor}=="1fc9", ATTRS{idProduct}=="04d8", MODE="0660", GROUP="plugdev" > /etc/udev/rules.d/45-lasershark.rules

#Clone openlase repository
RUN git clone https://github.com/marcan/openlase.git
WORKDIR openlase
RUN mkdir build
WORKDIR build
RUN perl -i.bak -p -e's/add_subdirectory\(qplayvid\)//g' ../tools/CMakeLists.txt
RUN cat ../tools/CMakeLists.txt
RUN cmake ..
RUN make

RUN apt-get -y install qjackctl

#install VNC
# Install vnc, xvfb in order to create a 'fake' display and firefox
run     apt-get install -y x11vnc xvfb
run     mkdir /.vnc
# Setup a password
run     x11vnc -storepasswd 1234 ~/.vnc/passwd
