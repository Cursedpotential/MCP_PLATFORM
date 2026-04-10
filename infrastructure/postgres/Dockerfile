FROM docker.io/pgvector/pgvector:pg16

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    git \
    libcurl4-openssl-dev \
    libjson-c-dev \
    pkg-config \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Optional extension compilation belongs here when we turn on the full
# federated-storage image in WSL/podman. The bootstrap SQL only enables
# extensions that are actually present in the image.
