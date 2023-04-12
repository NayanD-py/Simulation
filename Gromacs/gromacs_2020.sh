#!/usr/bin/bash

# Gromacs Shell Script for Installing Gromacs with GPU: 

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


#Download Gromacs 2020.7
wget -c -N https://ftp.gromacs.org/gromacs/gromacs-2020.7.tar.gz
tar -zxvf gromacs-2020.7.tar.gz


# Install Gromacs  2020.7
# Cmake parameter
#   -DGMX_GPU=CUDA
#   -DREGRESSIONTEST_DOWNLOAD=ON
#   -DGMX_GPU=OFF
#   -DCMAKE_INSTALL_PREFIX=path/to/install
#   

mkdir ./gromacs-2020.7/build
cd ./gromacs-2020.7/build
cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON -DGMX_GPU=CUDA
make
yes y | sudo make install



source /usr/local/gromacs/bin/GMXRC
gmx -h

