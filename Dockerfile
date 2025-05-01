Use a base image with Ubuntu
FROM ubuntu:20.04
# Set environment variables for CUDA
ENV LANG C.UTF-8
ENV CUDA_VERSION 11.4
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
RUN curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-11-4_11.4.0-1_amd64.deb -O && \
    dpkg -i cuda-11-4_11.4.0-1_amd64.deb && \
    apt-get update && \
    apt-get install -y cuda && \
    rm cuda-11-4_11.4.0-1_amd64.deb

# Install NVIDIA drivers (optional, only if needed in container)
# Uncomment if necessary. This should typically be handled outside Docker on the host.
# RUN apt-get install -y nvidia-driver-460

# Set up environment for CUDA
ENV PATH /usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Verify CUDA installation
RUN nvcc --version

# Clone the repositories and set up the environment
RUN git clone https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode /NvidiaWarp-GarmentCode
RUN git clone https://github.com/maria-korosteleva/GarmentCode /GarmentCode

# Run build_lib.py to build necessary libraries for NvidiaWarp-GarmentCode
WORKDIR /NvidiaWarp-GarmentCode
RUN python3 build_lib.py --cuda_path="/usr/local/cuda"

# Install required Python packages inside the GarmentCode directory
WORKDIR /GarmentCode
RUN pip3 install numpy scipy pyaml svgwrite psutil matplotlib svgpathtools cairosvg nicegui trimesh libigl pyrender cgal google.genai

# Install NvidiaWarp-GarmentCode as editable
WORKDIR /GarmentCode
RUN pip3 install -e /NvidiaWarp-GarmentCode

# Set the default command to run the GUI
CMD ["python3", "gui.py"]
