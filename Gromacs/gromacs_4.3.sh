#!/usr/bin/bash

# Gromacs Shell Script for Installing Gromacs: 

# Cmake-3.24.3 Download and Install
sudo apt-get install --fix-missing

sudo apt-get install g++ gcc make -y
sudo apt install  libssl-dev mesa-common-dev libglu1-mesa-dev -y
sudo apt-get install git build-essential libxml2-dev qt5-default libpqxx-dev libpq-dev libqt5svg5-dev qttools5-dev

#Download CMake
%%bash
wget -c -N https://github.com/Kitware/CMake/releases/download/v3.24.3/cmake-3.24.3.tar.gz
tar -zxvf cmake-3.24.3.tar.gz

# Installing CMake
cd cmake-3.24.3
./bootstrap
make
yes y | sudo make install



#Download Gromacs 4.5.3
wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-4.5.3.tar.gz
tar xzf gromacs-4.5.3.tar.gz

# Install Gromacs  4.5.3
# Cmake parameter
#   -DGMX_GPU=CUDA
#   -DGMX_GPU=OFF
#   -DCMAKE_INSTALL_PREFIX=path/to/install

mkdir ./gromacs-4.5.3/build
cd ./gromacs-4.5.3/build
cmake .. -DGMX_BUILD_OWN_FFTW=ON  -DGMX_GPU=CUDA
make -j 2  # number of cpu to use
yes y | sudo make install


source /usr/local/gromacs/bin/GMXRC
gmx -h

