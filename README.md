[//]: # (# Project Name)

[//]: # ()

[//]: # (**Author:** Your Name  )

[//]: # (**Date:** YYYY-MM-DD  )

[//]: # (**Version:** 1.0)

[//]: # ()

[//]: # (---)

[//]: # ()

[//]: # (## Table of Contents)

[//]: # ()

[//]: # (- [Project Overview]&#40;#project-overview&#41;)

[//]: # (- [Folder Structure]&#40;#folder-structure&#41;)

[//]: # (- [Requirements]&#40;#requirements&#41;)

[//]: # (- [Installation]&#40;#installation&#41;)

[//]: # (- [Usage]&#40;#usage&#41;)

[//]: # (- [Configuration]&#40;#configuration&#41;)

[//]: # (- [Contributing]&#40;#contributing&#41;)

[//]: # (- [License]&#40;#license&#41;)

[//]: # ()

[//]: # (---)

[//]: # ()

[//]: # (## Project Overview)

[//]: # ()

[//]: # (### Description)

[//]: # ()

[//]: # (Provide a brief summary of the project here.  )

[//]: # (Example: This project is designed to [do something specific], helping users to [achieve a particular outcome]. By)

[//]: # (implementing [specific technologies or methodologies], this project ensures efficient and reliable performance)

[//]: # (in [context or application].)

[//]: # ()

[//]: # (### Key Features)

[//]: # ()

[//]: # (- Feature 1: Briefly describe feature.)

[//]: # (- Feature 2: Briefly describe feature.)

[//]: # (- Feature 3: Briefly describe feature.)

[//]: # ()

[//]: # (---)

[//]: # ()

[//]: # (## Folder Structure)

[//]: # ()

[//]: # (```plaintext)

[//]: # (project-name/)

[//]: # (├── src/                  # Source code and main modules)

[//]: # (│   ├── module1.py)

[//]: # (│   ├── module2.py)

[//]: # (│   └── ...)

[//]: # (├── tests/                # Unit and integration tests)

[//]: # (│   ├── test_module1.py)

[//]: # (│   └── ...)

[//]: # (├── config/               # Configuration files)

[//]: # (│   └── config.yaml)

[//]: # (├── data/                 # Data directory)

[//]: # (│   ├── input/            # Input datasets)

[//]: # (│   └── output/           # Output files and results)

[//]: # (├── docs/                 # Documentation files)

[//]: # (│   └── README.md         # Project documentation)

[//]: # (├── scripts/              # Utility scripts)

[//]: # (│   ├── setup.sh          # Setup and installation script)

[//]: # (│   └── ...)

[//]: # (├── requirements.txt      # Python dependencies)

[//]: # (└── README.md             # Project overview and instructions)

# Marsifier

**Author:** [Yahav Gabay]  
**Date:** 2024-11-11
**Version:** 3.0

---

## Table of Contents

- [Project Overview](#project-overview)
- [Folder Structure](#folder-structure)
- [Design Patterns](#patterns)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)

---

## Project Overview

### Description

Marsifier is designed to provide specific functionality, e.g., process data, interact with APIs, automate tasks.
It aims to help users achieve specific goals, like data analysis, efficient data processing by
using relevant technologies and methodologies.

### Key Features

- **Modular Pipeline**: Easily configure and run data processing pipelines.
- **Database Interaction**: Supports multiple database connections and operations.
- **Data Receiving & Sending**: Modular components for data ingestion and exporting.

---

### Workflow

- If a file’s first half arrives, store its identifier in Redis.
- If the second half arrives, combine with the first, send to FastAPI, and delete both.
- Scan the folder initially for existing files; remove orphan files after 1 minute.

## Folder Structure

```plaintext
marsifier/
├── configurations/         # Configuration files for deployment, logging, and application settings
│   ├── ansible/            # Ansible playbooks for automated deployments
│   ├── config_models/      # Configuration model definitions
│   └── app.yml             # Main application config file
├── deployment/             # Deployment scripts and resources
├── src/                    # Source code and main application modules
│   ├── database/           # Database interaction handlers and templates
│   ├── pipeline_runner/    # Pipeline execution logic
│   ├── receiver/           # Data ingestion handlers
│   ├── sender/             # Data sending handlers
│   └── utils/              # Utility functions and helpers
├── requirements.txt        # Python dependencies
└── README.md               # Project overview and instructions
```
## Design Patterns

### Inversion of Control (IoC)
```
Pattern Type: Structural

Description: Inversion of Control (IoC) is a design principle in which the control of objects or portions of a program is transferred to a container or framework. In this project, IoC is implemented using a container that manages the lifecycle and dependencies of services and components.

Instead of manually creating and managing instances of classes, IoC relies on a central container to handle the instantiation, initialization, and dependency resolution for services. This leads to loose coupling and makes the system easier to test and maintain.

How it works:

Services are registered with a container, which is responsible for instantiating them and resolving any dependencies they might have.
Dependencies for services are injected automatically via decorators like @Inject or through constructor injection when a service is created.
When a function or class requires a service, the container resolves the service, injects its dependencies, and calls the function or method.
Implementation:

A central Container class holds a registry of services and their dependencies.
Services can be registered manually or automatically (e.g., through a decorator).
The container can then resolve these dependencies when required.
Example:
```


```python
class Container:
    def __init__(self):
        self._services = {}

    def register(self, name, service):
        self._services[name] = service

    def get(self, name):
        return self._services[name]()

container = Container()
```

```
Dependency Injection (DI)
Pattern Type: Structural

Description: The Dependency Injection pattern is used throughout the project to manage class dependencies and reduce tight coupling between components. DI is employed through a service container, which automatically injects the necessary dependencies into classes and functions.

#### Implementation:

The container stores services and manages their instantiation.
Services are automatically injected into class methods or standalone
 functions via decorators (@Inject).
Allows for easier testing and configuration of services.
Example:
```
```python
class MyService:
    @Inject("Database")
    def my_method(self, database):
        # database is injected automatically
        pass
```
### Factory Pattern
```

Pattern Type: Creational

Description: The Factory Pattern is used to create different objects based on a configuration, especially for services or handlers. This pattern ensures that object creation is encapsulated and centralized, making the system extensible.

Implementation:

Factory functions or classes are used to generate objects with varying configurations or behaviors.
Factories provide a unified interface for creating objects.
Example:
```
```python

class PoolFactory:
    @staticmethod
    def create_pool_strategy(pool_type, max_workers):
        # Factory method to return the appropriate pool strategy based on configuration
        if pool_type == "thread":
            return ThreadPool(max_workers)
        elif pool_type == "process":
            return ProcessPool(max_workers)
        else:
            raise ValueError("Unsupported pool type")
```

## Requirements
- **VMs**:
    - 4 VMs with `lftp` installed, configured for multi-process transfers.
    - 1 VM with `pure-ftpd` and `redis` and `filebeat` for file reception.

## Installation

## Continuous Deployment (CD) with Ansible

Marsifier includes an Ansible-based CD pipeline that automates deployment across all required VMs. Ansible playbooks in
the `configurations/ansible` folder handle:

- Installing dependencies
- Install packages listed in `deployment/requirements.txt`.
- Setting up each VM with necessary software

## Usage

#### To run the project, simply execute the main Ansible playbook:

```bash
ansible-playbook configurations/ansible/deploy.yml
```

## Configuration

#### environment vars that need to be configured

```bash

  APP_CONFIG_PATH: configurations/app.yml
  ENV: production
  LOG_CONFIG_PATH: configurations/logger.yml
```

## Contributing
 Shani hahofefet & my-eitan