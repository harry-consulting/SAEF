# Introduction 
SAEF means Self-Adaptive ETL Flow.

The SAEF project creates a quality control and monitoring tool for pipelines and jobs running in data warehouse, business intelligence, big data and machine learning applications. The design concept of SAEF is to consider different datasets generated in different steps of a data pipeline as "observation points". Similar to how electricians use voltage testers to inspect different circuits in a wire installation, SAEF considers each of the "observation points" as the place to plant programs that mines the profiles and patterns of the dataset at each point. By cross-checking the results at different points as well their historical values, it becomes easier to detect the anomalies and state of quality. Furthermore, when these programs are running in real time as part of the actual data pipeline, profiles and patterns found at each point can in fact decide if the flow should stop or how the flow should proceed. In this way, the execution of the data pipelines becomes a "self-controlling" and "self-adaptive" process. SAEF provides the engine to execute this process.

This first committed version in GitHub is a prototype version of SAEF. Basic functionalities such as dashboard, metadata registration, and RESTAPIs are made ready with its first version. We are working towards a "production-ready" version with more solid and consistent UI behavior and support of scheduling as well as alerting functionalities for users. 

# Getting Started

SAEF is a web-based application based on python, django framework and postgres. It is typically deployed in a VM or container in the cloud environment. In an on-prem environment, SAEF can also be deployed to a VM and provide services that connect to other applications in the same network. 

To install SAEF, following one of the three provided PDF files in the "doc" folder. 
1. "Setting Up Development Environment on Linux - Overview.pdf"
2. "Setting Up Development Environment on macOS - Overview.pdf"
3. "Setting Up Development Environment on Windows - Overview.pdf"

# Build and Test
The core project "saefportal" is based on django framework. It is used and can be built as a standard django application. Django test is used as the testing tool for all test cases created in SAEF. 

# Contribute
Use the document "CONTRIBUTING.md" as a guideline before making any contributions. 