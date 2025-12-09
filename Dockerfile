FROM python:3.10-slim

# Prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/mage2gen

# Copy source code into image
COPY . /opt/mage2gen

# Install dependencies
RUN pip install --no-cache-dir typer jinja2

# --- NEW: Fix Permissions ---
# Allow any user (host user) to write to the directory
# This fixes permission errors for pycache and test artifacts
RUN chmod -R 777 /opt/mage2gen
# ----------------------------

# Set python path so module is resolvable
ENV PYTHONPATH="/opt/mage2gen"

# Entrypoint allows arguments to be passed directly
ENTRYPOINT ["python3", "-m", "mage2gen.app"]