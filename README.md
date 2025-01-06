# Welcome to instagram project!
RESTful API created using FastAPI. The app works as a server and provides CRUD operations for managing iamges, posts, tags, comments, scores, users and other entities.
The project supposrts asynchronous operation, works with the database via SQLAlchemy, and can be run in a Docker container.
# Features
- Asynchronous API: Maintain high performance with FastAPI.
- Authentication: Support registration, login, and role management.
- ORM: SQLAlchemy is used to work with the database.
- Configuration: Using .env for environment variables.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Requirements
Before you start, make sure you have everything installed:
- Python 3.10+
- Poetry for dependency management
- Docker
  
## Installation
1. Clone the repository:
```bash
 git clone https://github.com/Deminform/instagram_final_project.git
```
2. Setup virtual environment
```bash
poetry install
poetry shell
```
3. Create .env file in your root directory and fill it with necessary environment variables.
Use .env_example file as example

4. Run docker-compose.yml to connect to database and mail service locally
```bash
 docker compose up
 ```
5. Run alembic migrations to create database
```bash
alembic revision --autogenerate -m 'Init’
alembic upgrade head
```
6. Run migration to fill data in 'roles' table

## Usage
To run the project, use the following command:
```bash
fastapi dev main.py
```

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Push your branch: `git push origin feature-name`.
5. Create a pull request.

## Authors
[@Deminform](https://github.com/Deminform), [@volodymyr-v-konoval](https://github.com/volodymyr-v-konoval), [@ToshikAR](https://github.com/ToshikAR), [@marinasemak](https://github.com/marinasemak), [@BuDi4ka](https://github.com/BuDi4ka)

## License
Copyright © 2025

_This README was generated with ❤️ by 'Міцні Горіхи' team
