# PhotoShare REST API

Welcome to PhotoShare - a REST API project built using FastAPI.

## Introduction

PhotoShare is a versatile REST API application designed to facilitate photo sharing and commenting among users. Leveraging the power of FastAPI, it provides robust functionality for managing images, adding comments, and ensuring secure user authentication.

## Technologies we use

Python, Poetry, Postgres, SQLAlchemy, Alembic, Redis

## Features

- JWT token-based authentication.
- Supports three user roles: standard user, moderator, and administrator.
- The first user registered is always assigned the administrator role.
- Users can upload photos with descriptions.
- Users can delete their uploaded photos.
- Users can edit photo descriptions.
- Users can retrieve photos using a unique link.
- Ability to add up to 5 tags per photo and optional Tags.
- Users can generate links for transformed images to display as URLs and QR codes.
- Users can comment on photos uploaded by other users.
- Users can edit their comments but cannot delete them.
- Moderators and administrators have the privilege to delete comments.
- Comments are stored in the database with creation and update timestamps.
- Route to a user's profile based on their unique username.
- You can edit your information and view information about yourself.
- The administrator can deactivate (ban) users.
- The user can search for photos by keywords or tags. After searching, the user can filter the results by rating or date added.
- Moderators and administrators can search and filter by users who have added photos.

## Setup

1. Clone the repository:
   `git clone https://github.com/yourusername/photoshare.git`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Set up environment variables for database connection, Cloudinary API, and JWT secret key.
4. Run the application:
   `uvicorn main:app --reload`

## Usage

- Register an account and obtain JWT token for authentication.
- Explore endpoints for uploading, managing, and commenting on photos.
- Utilize Cloudinary transformations for image operations.
- Leverage QR code generation for sharing transformed images.
- Administrators can perform CRUD operations on user photos and comments.

## TODO

In future we will deploy this project somewhere in order to make it more avialable to a typical user of internet

## Contributing

Contributions are welcome! Please follow the Contribution Guidelines.

## License

This project should be licensed under the MIT License.

## Project Structure

```
photo_share
├─ .gitignore
├─ alembic
│  ├─ env.py
│  ├─ README
│  ├─ script.py.mako
│  └─ versions
│     ├─ 0e447b4659f7_update_bool_level.py
│     └─ d4b9334092ad_start_project.py
├─ alembic.ini
├─ main.py
├─ poetry.lock
├─ pyproject.toml
├─ README.md
├─ src
│  ├─ conf
│  │  ├─ config.py
│  │  └─ __init__.py
│  ├─ database
│  │  ├─ db.py
│  │  ├─ models.py
│  │  └─ __init__.py
│  ├─ repository
│  │  ├─ users.py
│  │  └─ __init__.py
│  ├─ routes
│  │  ├─ auth.py
│  │  ├─ users.py
│  │  └─ __init__.py
│  ├─ schemas.py
│  ├─ services
│  │  ├─ auth.py
│  │  ├─ email.py
│  │  ├─ templates
│  │  │  ├─ email_template.html
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  └─ __init__.py
└─ tests
   └─ __init__.py
```
