# Simple REST API with Java Spring Boot

A complete REST API built with Spring Boot that provides CRUD operations for managing users.

## Features

- **GET** - Retrieve all users or a specific user by ID/email
- **POST** - Create new users
- **PUT** - Update existing users
- **DELETE** - Remove users
- **H2 In-Memory Database** - For development and testing
- **Input Validation** - Bean validation for data integrity
- **Error Handling** - Proper HTTP status codes and error messages
- **CORS Support** - Cross-origin resource sharing enabled

## Prerequisites

- Java 8 or higher
- Maven 3.6 or higher

## Getting Started

### 1. Clone and Navigate to Project
```bash
cd java-services
```

### 2. Build the Project
```bash
mvn clean install
```

### 3. Run the Application
```bash
mvn spring-boot:run
```

The application will start on `http://localhost:60001`

**Note:** If you need to change the port, you can either:
- Edit `src/main/resources/application.properties` and change `server.port=60001` to your desired port
- Or run with command line argument: `mvn spring-boot:run -Dspring-boot.run.arguments="--server.port=YOUR_PORT"`

## API Endpoints

### Base URL
```
http://localhost:60001/api/users
```

### 1. GET All Users
```http
GET /api/users
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "description": "Software Developer"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "description": "Product Manager"
  }
]
```

### 2. GET User by ID
```http
GET /api/users/{id}
```

**Example:**
```http
GET /api/users/1
```

### 3. GET User by Email
```http
GET /api/users/email/{email}
```

**Example:**
```http
GET /api/users/email/john.doe@example.com
```

### 4. POST Create User
```http
POST /api/users
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "description": "New team member"
}
```

**Response:** 201 Created
```json
{
  "id": 6,
  "name": "New User",
  "email": "newuser@example.com",
  "description": "New team member"
}
```

### 5. PUT Update User
```http
PUT /api/users/{id}
Content-Type: application/json
```

**Example:**
```http
PUT /api/users/1
```

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "email": "john.doe.updated@example.com",
  "description": "Senior Software Developer"
}
```

### 6. DELETE User
```http
DELETE /api/users/{id}
```

**Example:**
```http
DELETE /api/users/1
```

**Response:** 204 No Content

### 7. Health Check
```http
GET /api/users/health
```

**Response:**
```
User API is running!
```

## Database

The application uses H2 in-memory database for development:

- **H2 Console:** http://localhost:60001/h2-console
- **JDBC URL:** jdbc:h2:mem:testdb
- **Username:** sa
- **Password:** password

## Sample Data

The application automatically creates 5 sample users on startup:

1. John Doe (john.doe@example.com) - Software Developer
2. Jane Smith (jane.smith@example.com) - Product Manager
3. Bob Johnson (bob.johnson@example.com) - Data Analyst
4. Alice Brown (alice.brown@example.com) - UX Designer
5. Charlie Wilson (charlie.wilson@example.com) - DevOps Engineer

## Validation Rules

- **Name:** Required, 2-50 characters
- **Email:** Required, valid email format, unique
- **Description:** Optional, max 200 characters

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK** - Successful GET/PUT operations
- **201 Created** - Successful POST operations
- **204 No Content** - Successful DELETE operations
- **400 Bad Request** - Validation errors or business logic violations
- **404 Not Found** - Resource not found

## Testing with cURL

### Get all users
```bash
curl -X GET http://localhost:60001/api/users
```

### Get user by ID
```bash
curl -X GET http://localhost:60001/api/users/1
```

### Create a new user
```bash
curl -X POST http://localhost:60001/api/users \
```
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "description": "Test description"
  }'
```

### Update a user
```bash
curl -X PUT http://localhost:60001/api/users/1 \
```
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "email": "updated@example.com",
    "description": "Updated description"
  }'
```

### Delete a user
```bash
curl -X DELETE http://localhost:60001/api/users/1
```

## Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── restapi/
│   │               ├── RestApiApplication.java
│   │               ├── controller/
│   │               │   └── UserController.java
│   │               ├── model/
│   │               │   └── User.java
│   │               ├── repository/
│   │               │   └── UserRepository.java
│   │               ├── service/
│   │               │   └── UserService.java
│   │               └── config/
│   │                   └── DataInitializer.java
│   └── resources/
│       └── application.properties
└── test/
    └── java/
        └── com/
            └── example/
                └── restapi/
                    └── RestApiApplicationTests.java
```

## Technologies Used

- **Spring Boot 3.2.0** - Main framework
- **Spring Data JPA** - Data access layer
- **H2 Database** - In-memory database
- **Bean Validation** - Input validation
- **Maven** - Build tool and dependency management

## Next Steps

To extend this API, you could:

1. Add authentication and authorization
2. Implement pagination for large datasets
3. Add more complex search and filtering
4. Integrate with a production database (PostgreSQL, MySQL)
5. Add unit and integration tests
6. Implement API documentation with Swagger/OpenAPI
7. Add logging and monitoring
8. Implement caching with Redis
