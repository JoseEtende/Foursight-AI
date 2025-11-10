# Use the official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Reduce pip network flakiness in containers
ENV PIP_DEFAULT_TIMEOUT=120 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_ROOT_USER_ACTION=ignore

# Copy the requirements file and install dependencies
COPY services/orchestrator_agent/requirements.txt services/orchestrator_agent/constraints.txt ./
# Install system-level dependencies for numpy/scikit-learn if needed
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Copy the agent application code
COPY services/orchestrator_agent/app/ app/

# Copy the main entrypoint script
COPY services/orchestrator_agent/main.py .

# Set the command to run the custom server entrypoint
CMD ["python", "main.py"]
