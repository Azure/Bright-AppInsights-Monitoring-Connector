# Bright-AppInsights-Monitoring-Connector

Sample code to push monitoring data from Bright cluster to Application Insights.

## Contents

Outline the file contents of the repository. It helps users navigate the codebase, build configuration and any related assets.

| File/folder       | Description                                |
|-------------------|--------------------------------------------|
| `src`             | Source code.                        |
| `.gitignore`      | Define what to ignore at commit time.      |
| `CHANGELOG.md`    | List of changes to the sample.             |
| `CONTRIBUTING.md` | Guidelines for contributing to the sample. |
| `README.md`       | This README file.                          |
| `LICENSE`         | The license for the sample.                |

## Prerequisites

1. Docker installed
2. Application Insights Instrumentation Key
3. Bright Head node Host IP
4. Bright connection certificates with has authorized for CMMon service

## Setup

1. Configure BrightHostIP and InstrumentationKey in Bright-AppInsights-Monitoring-Connector/appconfig.json
2. Configure Necessary Metrics inb Bright-AppInsights-Monitoring-Connector/metricconfig.ini
3. Add pem and key to Bright-AppInsights-Monitoring-Connector/certs as bright-cert.pem and bright-key.key respectively

## Running the sample

    # go to project dir
    cd Bright-AppInsights-Monitoring-Connector
    
    # build docker image
    docker build --tag='appinsights-monitoring' .
    
    # run docker image
    docker run -d appinsights-monitoring
    
## Create sample Dashboard graph

1. Go to your Application Insights workspace
2. Go to Logs (Analytics)
3. Run below command (It may take few minutes to reflect metric data to application insights)

    `
        traces
            | summarize timestamp = min(timestamp) by tostring(message)
            | extend nodeinfo = parse_json(message)
            | extend hostname = tostring(nodeinfo.Hostname) 
            | extend cpuidle = toreal(nodeinfo.CPUIdle)
            | project TimeStamp = timestamp, Hostname = hostname, CPUUsage = cpuidle 
            | render timechart 
    `

4. Click Pin to Dashboard to add the graph to Azure Dashboards

## How to Debug

Run below command to check application logs

    docker exec <docker-container-id> tail -20 Trace_log.log

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
