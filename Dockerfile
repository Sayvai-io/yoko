# FROM ubuntu:20.04
FROM nvidia/cuda:12.9.0-devel-ubuntu24.04

ENV LANG C.UTF-8
ENV CUDA_VERSION 12.9
ENV PATH /usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV DEBIAN_FRONTEND=noninteractive


# Install base dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Clone NvidiaWarp-GarmentCode
RUN git clone https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode /NvidiaWarp-GarmentCode

# If your project is local, copy it in (if needed)
COPY . /GarmentCode

# Or clone if it's remote
# RUN git clone https://github.com/maria-korosteleva/GarmentCode /GarmentCode

# Install pygarment and other packages
WORKDIR /GarmentCode
RUN pip3 install -r requirements.txt

# Build native libraries
WORKDIR /NvidiaWarp-GarmentCode
RUN python3 build_lib.py --cuda_path="/usr/local/cuda"

# Install the package in editable mode
WORKDIR /GarmentCode
RUN pip3 install -e /NvidiaWarp-GarmentCode

ENV PORT 3000
EXPOSE 3000
CMD ["python3", "gui.py"]
