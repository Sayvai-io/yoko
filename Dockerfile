# FROM ubuntu:20.04
FROM nvidia/cuda:12.9.0-devel-ubuntu24.04

ENV LANG C.UTF-8
ENV CUDA_VERSION 12.9
ENV PATH /usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/GarmentCode/venv


# Install base dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    libcairo2 \
    build-essential \
    ca-certificates \
    libomp-dev \
    wget \
    curl \
    gnupg2 \
    lsb-release \
    cron \
    mysql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl-mesa0 \
    libgl1 \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libgles2 \
    libx11-6 \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# Clone NvidiaWarp-GarmentCode
RUN git clone https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode /NvidiaWarp-GarmentCode

# If your project is local, copy it in (if needed)
COPY . /GarmentCode

WORKDIR /GarmentCode
RUN python3 -m venv venv

# Or clone if it's remote
# RUN git clone https://github.com/... /GarmentCode

# Install pygarment and other packages
WORKDIR /GarmentCode
RUN /GarmentCode/venv/bin/pip install --upgrade pip && \
    /GarmentCode/venv/bin/pip install -r requirements.txt

# Build native libraries
WORKDIR /NvidiaWarp-GarmentCode
RUN chmod +x ./tools/packman/packman
WORKDIR /NvidiaWarp-GarmentCode
RUN /GarmentCode/venv/bin/python build_lib.py --cuda_path="/usr/local/cuda"

# Install the package in editable mode
WORKDIR /GarmentCode
RUN /GarmentCode/venv/bin/pip install -e /NvidiaWarp-GarmentCode

# Set up cron job for database backup
COPY db-backup-cron-app/db-cron.py /GarmentCode/db-backup-cron-app/
RUN chmod +x /GarmentCode/db-backup-cron-app/db-cron.py

# Create cron job to run backup every day at 2 AM (0 2 * * *)
RUN echo "* * * * * cd /GarmentCode && /GarmentCode/venv/bin/python db-backup-cron-app/db-cron.py >> /var/log/cron.log 2>&1" > /etc/cron.d/db-backup-cron
RUN chmod 0644 /etc/cron.d/db-backup-cron

# Create log file for cron
RUN touch /var/log/cron.log

# Start cron service and the main application
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV PORT 3000
EXPOSE 3000
CMD ["/start.sh"]
