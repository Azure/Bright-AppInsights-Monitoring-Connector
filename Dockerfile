# Use python 3.6.7
FROM python:3.6.7-slim

# Setting up working directory
WORKDIR /Workspace/Bright-AppInsights-Monitoring-Connector

# Copy project area
COPY . /Workspace/Bright-AppInsights-Monitoring-Connector

# Installing required python packages
RUN python3.6 -m pip install --upgrade pip
RUN python3.6 -m pip install --no-cache-dir --trusted-host pypi.python.org -r /Workspace/Bright-AppInsights-Monitoring-Connector/requirements.txt

# Downloading pythoncm package
RUN apt-get update && apt-get -yq install wget
RUN cd /usr/src/ && wget -O pythoncm.tar.gz "https://support2.brightcomputing.com/koen/pythoncm/pythoncm-82-py3-138113_cm8.2_b9830fedee.tar.gz"
RUN cd /usr/src/ && tar xvzf pythoncm.tar.gz
RUN cd /usr/src/ && mv pythoncm/ /usr/local/lib/python3.6/site-packages/

CMD ["/usr/local/bin/python3.6", "/Workspace/Bright-AppInsights-Monitoring-Connector/src/main.py", "--emit-interval", "5", "--refresh-interval", "1440"]
