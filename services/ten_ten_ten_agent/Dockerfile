# Use the official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Reduce pip network flakiness in containers
ENV PIP_DEFAULT_TIMEOUT=120 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_ROOT_USER_ACTION=ignore

# Copy the requirements file and install dependencies
COPY services/ten_ten_ten_agent/requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the agent application code
COPY services/ten_ten_ten_agent/app/ app/

# Copy the knowledge base
# This path must match the one used in load_knowledge_base()
COPY scripts/ /scripts/

# Set the command to run the ADK web server
# The ADK web server will automatically find the 'app' directory
CMD ["adk", "api_server", "--host", "0.0.0.0", "--port", "8080"]