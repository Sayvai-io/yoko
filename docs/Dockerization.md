# Installation

## Local paths setup

Clone the repository now [Yoko/GarmentCode](https://github.com/Sayvai-io/yoko.git)

    git clone https://github.com/Sayvai-io/yoko.git
    cd yoko

## Steps to dockerize

### 1. Create .env as mentioned in .env.example file
### 2. Add service_account.json in project

if service_account.json is not yet generated, follow these steps [Steps to generate](../db-backup-cron-app/README.md)

### 3. Configure system.template.json values (Optional)

### 4. Make sure your are inside our project repo

cd /path/to/project

### 5. Make sure docker-compose.yaml exists, Then Run

    docker compose up

build starts and the applications runs at PORT 3000.
