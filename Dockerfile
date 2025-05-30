FROM ubuntu:24.04

ENV LANG C.UTF-8
ENV CUDA_VERSION 12.9
ENV PATH /usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/venv

# Configure apt
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::ftp::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries

# Install base dependencies with retry logic
RUN for i in $(seq 1 3); do \
    apt-get update && \
    apt-get install -y --no-install-recommends \
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
        mysql-client && \
    break || sleep 15; \
    done && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl-mesa0 \
    libgl1 \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libgles2 \
    libx11-6 \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# cuda installation starts
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
RUN mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
RUN wget https://developer.download.nvidia.com/compute/cuda/12.9.0/local_installers/cuda-repo-ubuntu2204-12-9-local_12.9.0-575.51.03-1_amd64.deb
RUN dpkg -i cuda-repo-ubuntu2204-12-9-local_12.9.0-575.51.03-1_amd64.deb
RUN cp /var/cuda-repo-ubuntu2204-12-9-local/cuda-*-keyring.gpg /usr/share/keyrings/
RUN apt-get update
RUN apt-get -y install cuda-toolkit-12-9
# cuda installation ends

# Create and activate virtual environment
RUN python3 -m venv /venv

# Install pygarment and other packages
RUN /venv/bin/pip install --upgrade pip && \
/venv/bin/pip install pygarment

# # Clone NvidiaWarp-GarmentCode
RUN git clone https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode /NvidiaWarp-GarmentCode

COPY . /GarmentCode

RUN mv /GarmentCode/system.json /GarmentCode/system.json

COPY ./service_account.json /service_account.json

# Install pygarment and other packages
RUN /venv/bin/pip install -r /GarmentCode/requirements.txt

# # Build native libraries
WORKDIR /NvidiaWarp-GarmentCode
RUN chmod +x ./tools/packman/packman

# WORKDIR /NvidiaWarp-GarmentCode
RUN /venv/bin/python build_lib.py --cuda_path="/usr/local/cuda"

RUN /venv/bin/pip install -e /NvidiaWarp-GarmentCode

# # Set up cron job for database backup
COPY db-backup-cron-app/db-cron.py /GarmentCode/db-backup-cron-app/
RUN chmod +x /GarmentCode/db-backup-cron-app/db-cron.py

# Create cron job to run backup every day at 2 AM (0 2 * * *)
RUN printf "SHELL=/bin/bash\nPATH=/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nPYTHONPATH=/GarmentCode\n\n0 2 * * * root cd /GarmentCode && /venv/bin/python db-backup-cron-app/db-cron.py >> /var/log/cron.log 2>&1\n" > /etc/cron.d/db-backup-cron \
 && chmod 0644 /etc/cron.d/db-backup-cron

# Create log file for cron
RUN touch /var/log/cron.log

# Start cron service and the main application
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV PORT 3000
EXPOSE 3000
CMD ["/start.sh"]
