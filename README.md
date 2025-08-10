
# Task Management System

A comprehensive Django-based task management application that allows users to organize, track, and manage their tasks efficiently with priority-based organization.

## Features

### User Authentication
- **User Registration**: Sign up with email verification (OTP-based) or without OTP
- **Secure Login**: JWT-based authentication with session management
- **Profile Management**: Update user profile information

### Task Management
- **Create Tasks**: Add tasks with date scheduling and priority levels
- **Priority System**: Organize tasks by priority (High, Medium, Low)
- **Date-based Organization**: Schedule tasks for specific dates
- **Status Tracking**: Track task progress with multiple status options:
  - Pending
  - In Progress
  - Completed



### Task Operations
- **Update Tasks**: Modify task details, dates, and priorities
- **Delete Tasks**: Remove completed or unnecessary tasks
- **Status Management**: Change task status as work progresses




## Installation

### Prerequisites
```- Python 3.8+
- PostgreSQL
- pip (Python package manager)
```
### Setup Instructions

1. **Clone the repository**
   ```
   - git clone <repository-url>
   - cd task-management

   ```

2. **Create virtual environment**
   ``` 
   - python -m venv venv
   - source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```

3. **Install dependencies**
   ```
   - pip install -r requirements.txt

   ```
4. **Environment Configuration**

   - Create a `.env` file in the project root:
      ```env
      SECRET_KEY=your-secret-key-here
      DEBUG=True
      
      # Database Configuration
      DATABASE_NAME=your_database_name
      DATABASE_USER=your_database_user
      DATABASE_PASSWORD=your_database_password
      DATABASE_HOST=localhost
      DATABASE_PORT=5432
      
      # Email Configuration
      EMAIL_HOST=smtp.gmail.com
      EMAIL_PORT=587
      EMAIL_HOST_USER=your-email@gmail.com
      EMAIL_HOST_PASSWORD=your-app-password
      ```

5. **Database Setup**
   ```
   - python manage.py migrate

   ```

   
   

6. **Run Development Server**
   ```
   - python manage.py runserver

   ```

## Configuration

### Database
The application uses PostgreSQL as the primary database. Ensure PostgreSQL is installed and running on your system.

### Email Configuration
Email functionality is configured for OTP verification during registration. Update the email settings in your `.env` file with your SMTP credentials.
