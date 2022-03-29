# Introduction 
SAEF means Self-Adaptive ETL Flow.
 
The SAEF project creates a data lake system where the ETL, quality control and data profiling are handled automatically by the internal system. Users of SAEF only need to focus on using the data, aka. browsing, querying, and fetching data. Further, it is easy to create and control jobs that update data.
 
The current release of SAEF is a fully functional version that runs on either a VM or a containerized environment. Users are free to deploy SAEF to any cloud environment and the cost is only on the compute and storage throughput charged by the cloud vendors.
 
# Getting Started
The front-end of SAEF is a web application based on django framework and postgres. It is typically deployed in a cloud environment but can also be configured to work on-prem.
 
# Build and Test
Django test is used as the testing tool for all test cases created in SAEF.
 
# Contribute
Use the document "CONTRIBUTING.md" as a guideline before making any contributions.

# License
All files in this project are released under the terms described LICENSE.md