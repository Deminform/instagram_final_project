# Welcome to PhotoShare!
PhotoShare is a photo-sharing web application developed with FastAPI, allowing users to upload, share, and interact with photos. The platform supports a variety of features including user authentication, photo transformations, and commenting. Users can upload photos, add tags, and share links with QR codes. The app integrates with Cloudinary for efficient image handling, enabling transformations like resizing and cropping. With roles for regular users, moderators, and administrators, PhotoShare provides robust access control.
# Features
- User Authentication: Register, log in, and manage user sessions with JWT tokens.
- Photo Management: Upload, delete, and edit photos, along with descriptions.
- Tags: Add and manage tags for photos. Tags are unique across the application.
- Photo Transformations: Choose from a limited set of Cloudinary transformations (resize, crop, etc.).
- QR Code Sharing: Generate unique URLs and QR codes for transformed photos.
- Comments: Comment on photos, with the ability to edit your own comments. Admins and moderators can delete comments.
- Rating: Rate photos from 1 to 5 stars, with an average rating displayed.
- Search & Filter: Search photos by keywords or tags and filter results by rating or date.
- Admin Controls: Admins can manage users (ban, deactivate) and perform CRUD operations on all photos.

## Technologies Used
- FastAPI for building the REST API.
- PostgreSQL for storing user, photo, and comment data.
- SQLAlchemy for database interactions.
- Cloudinary for image transformations.
- JWT for secure authentication and role-based access.
- Swagger UI for API documentation.

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
5. Run alembic migrations to create database and fill data in 'roles' table
```bash
alembic upgrade head
```
6. Run migration to fill data in 'roles' table

## Usage
To run the project, use the following command:
```bash
fastapi dev main.py
```

First user with admin role is created during startup with credentials, set in .env file:
```
ADMIN_EMAIL
ADMIN_PASSWORD
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
