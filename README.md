## NewWork HR Application

A modern, single-page HR application built with a React frontend and a Django backend. This project is designed to manage employee profiles, feedback, and absence requests with a role-based permission system.

The application is fully containerized with Docker for consistent and reliable deployments.

### Considerations
- This project is architected as decoupled Single Page Application using React (TS) and a Django REST API backend. This separation allows for independent development and scaling of the frontend and backend services.
- For the purposes of this demo, only one profile is viewed and edited in the frontend. Thus, some hardcoded values or IDs can be expected.
- The API implementation in Python leverages Django REST Framework, and it's viewSet/model to accelerate endpoint implementation.
- User authentication is handled via Django's built-in authentication system with token-based authentication, JWT, for API access (TokenPair).  Token refresh is implemented, but not fully integrated into the frontend for simplicity.
- Sensitive data and readonly fields are managed with Serializer instead of custom validators and more custom role-based permissions.
- The frontend uses React Context for state management (thus no global state management), avoiding more complex libraries like Redux for simplicity. Local storage is also used for simplicity.
- For deployment, the application is fully containerized using a multi-stage Docker build, ensuring a consistent environment.
- Future quick improvements could include adding unit and integration tests, enhancing error handling, and implementing more robust and persistent logging.
- Other quick improvements would be to have a profile navigator (or profile search page), more CRUD operations over Feedback and Absence requests, and others.

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
3. **Default Logins**

   The application is seeded with demo data. You can log in with:
   - Manager: manager@example.com / password123
   - Employee: john.smith@example.com / password123 
   - Co-worker: john.doe@example.com / password123

4. **API Documentation**
   - A Postman collection is available in the `docs/` directory for testing the API endpoints.
   - Once the backend is running, access the API documentation at:
     ```html
     http://localhost/api/schema/swagger-ui/
     or
     http://localhost:8000/api/schema/swagger-ui/ (if running backend separately)
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
---

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