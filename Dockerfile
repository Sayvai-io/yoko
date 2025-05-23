# Use a base image with Ubuntu
FROM ubuntu:20.04

# Set environment variables for CUDA
ENV LANG C.UTF-8
ENV CUDA_VERSION 12.9
ENV PATH /usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Install dependencies (you can add any other dependencies you need)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    build-essential \
    ca-certificates \
    libomp-dev \
    wget \
    curl \
    gnupg2 \
    lsb-release \
    && apt-get clean

# Install CUDA 11.4
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin && \
mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600 && \
wget https://developer.download.nvidia.com/compute/cuda/12.9.0/local_installers/cuda-repo-ubuntu2004-12-9-local_12.9.0-575.51.03-1_amd64.deb && \
dpkg -i cuda-repo-ubuntu2004-12-9-local_12.9.0-575.51.03-1_amd64.deb && \
cp /var/cuda-repo-ubuntu2004-12-9-local/cuda-*-keyring.gpg /usr/share/keyrings/ && \
apt-get update && \
apt-get -y install cuda-toolkit-12-9

# Set up environment for CUDA
ENV PATH /usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Clone the repositories and set up the environment
RUN git clone https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode /NvidiaWarp-GarmentCode
COPY . /GarmentCode

WORKDIR /GarmentCode

# Create and activate virtual environment, install requirements
RUN python3 -m venv venv && \
    /GarmentCode/venv/bin/pip install -r requirements.txt

# Build native libraries
WORKDIR /NvidiaWarp-GarmentCode
RUN /GarmentCode/venv/bin/python build_lib.py --cuda_path="/usr/local/cuda"

# Install NvidiaWarp-GarmentCode as editable
WORKDIR /GarmentCode
RUN /GarmentCode/venv/bin/pip install -e /NvidiaWarp-GarmentCode

ENV PORT 3000
EXPOSE 3000
CMD ["/GarmentCode/venv/bin/python", "gui.py"]
