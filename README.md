## NewWork HR Application

A modern, single-page HR application built with a React frontend and a Django backend. This project is designed to manage employee profiles, feedback, and absence requests with a role-based permission system.

The application is fully containerized with Docker for consistent and reliable deployments.

### Tech Stack
- Frontend: React 19, TypeScript, Vite, Material-UI 
- Backend: Python 3.13, Django 5+, Django REST Framework 
- Database: PostgreSQL 
- Deployment: Docker, Docker Compose, Nginx, Gunicorn 
- API Documentation: drf-spectacular (Swagger/OpenAPI)

### Pre-requisites
- Docker Compose
- Hugging Face API Key for AI functionalities
---

## Setup Instructions
1. **Clone the Repository**
    ```bash
      git clone https://github.com/RicardoMiranda7/newwork_hrapp.git
      cd newwork
    ```
2. **Environment Variables**
   - Create a `.env` file in the backend directory, `backend/.env`
   - Set your environment variables such as DB host and Hugging model api key.
       ```dotenv
        # backend/.env
        # Used ONLY when running the backend from your IDE
        DB_HOST=localhost
        HUGGING_FACE_API_KEY=API_KEY_HERE
        ```
---
## Running the Application
### Production Environment (Unified Build)
1. **Update Production Environment Variables**
    - Open the main docker-compose.yml file and add your Hugging Face API key.
       ```yml
        # docker-compose.yml
        services:
          app:
            # ...
            environment:
              # ... other vars
              - HUGGING_FACE_API_KEY=API_KEY_HERE # <-- ADD YOUR KEY HERE 
        ```
2. **Build and Run**
   - From the project root, run
     ```bash
     docker-compose up --build
     ```
3. **Access the Application**
   - Main App: http://localhost
   - Django Admin: http://localhost/admin/
   - API Documentation (Swagger): http://localhost/api/schema/swagger-ui/

4. **Stop the Application**
   - To stop the application, run:
      ```bash
      docker-compose down
      ```
5. **Default Logins**

    The application is seeded with demo data. You can log in with:
   - Manager: manager@example.com / password123 
   - Employee: john.smith@example.com / password123 
   - Co-worker: john.doe@example.com / password123


### Development Environment (Services Run in IDEs)
1. **Start the db, run migrations and seed demo data**
    - From the project root, run:
        ```bash
        docker-compose -f docker-compose.dev.yml up
        ```
2. **Start the backend from your IDE**
   - Open the backend/ directory in your Python IDE (e.g., PyCharm).
   - Run a Django development server on port `8000` and set `PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=newwork_backend.settings` and environment variables of the server configuration.
     ```bash
     docker-compose up --build
     ```
3. **Start the frontend from your IDE**
    - Open the frontend/ directory in your JavaScript IDE (e.g., VSCode or IDEA)
    - Install dependencies
        ```bash
        npm install
        ```
    - Start the Vite development server
        ```bash
        npm run dev
        ```
4. **Access the Application**
   - The frontend is now running at http://localhost:5173. The `frontend/.env.development` file correctly points it to the backend API at http://localhost:8000.
   - The backend is now running at http://localhost:8000. The `backend/.env` file correctly points it to the database at `localhost`