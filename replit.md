# Overview

Skillmate is a Django-based e-learning platform that enables instructors to create and upload online courses for students. The platform provides a comprehensive learning management system with user authentication, course management, enrollment tracking, and video content delivery. Built with Django 4.1.7, it leverages Cloudinary for media storage and django-allauth for authentication, including social login capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses a traditional server-side rendered approach with Django templates. The frontend is built with:
- **Template Engine**: Django's built-in template system with template inheritance through base templates
- **Static Assets**: CSS and JavaScript files served through Django's static file handling
- **Responsive Design**: CSS-based responsive layout with custom styling
- **User Interface**: Clean, modern interface with course cards, dashboard layouts, and form interfaces

## Backend Architecture
The backend follows Django's Model-View-Template (MVT) pattern:
- **Framework**: Django 4.1.7 with Python
- **URL Routing**: RESTful URL patterns organized by functionality (main app URLs, account URLs)
- **Views**: Function-based views handling course display, dashboard management, and user interactions
- **Models**: Three primary models - Course, Library, and Enrollment with relationships between users and courses
- **Forms**: Django ModelForms for course creation and editing

## Data Storage Solutions
- **Database**: SQLite (default Django database for development)
- **Media Storage**: Cloudinary integration for storing course thumbnails, featured videos, and lesson videos
- **File Handling**: CloudinaryField for seamless media upload and delivery
- **Data Relationships**: Many-to-many relationships between users and courses for enrollment tracking

## Authentication and Authorization
- **Authentication System**: Django-allauth for comprehensive user management
- **Social Authentication**: Google OAuth integration for social login
- **User Management**: Built-in Django User model with profile extensions
- **Access Control**: Login-required decorators for protected views and dashboard access
- **Session Management**: Django's built-in session framework

## Course Management System
- **Course Creation**: Instructors can upload courses with metadata, requirements, and content
- **Video Integration**: Support for featured videos and lesson videos through Cloudinary
- **Course Categorization**: Category-based course organization and filtering
- **Enrollment System**: Student enrollment tracking with many-to-many relationships
- **Dashboard**: Separate interfaces for instructors and students with relevant course information

## URL Structure and Navigation
- **Public Routes**: Home, about, contact, courses listing, and category filtering
- **Dashboard Routes**: Protected routes for course management, profile, enrollment tracking
- **Authentication Routes**: Login, signup, logout, and password reset functionality
- **Course Detail Routes**: Dynamic URLs for individual course pages and lesson viewing

# External Dependencies

## Core Framework Dependencies
- **Django 4.1.7**: Primary web framework
- **django-allauth 0.52.0**: Authentication and social account management
- **gunicorn 20.1.0**: WSGI HTTP server for deployment
- **whitenoise 6.4.0**: Static file serving for production

## Media and File Handling
- **cloudinary 1.32.0**: Cloud-based media storage and delivery service for course videos and images

## Development and Utility Libraries
- **python-dotenv**: Environment variable management
- **pytz 2023.2**: Timezone handling
- **requests 2.28.2**: HTTP library for external API calls
- **cryptography 39.0.2**: Cryptographic functionality for secure operations

## Database and ORM
- **sqlparse 0.4.3**: SQL parsing utilities
- **asgiref 3.6.0**: ASGI compatibility layer

## OAuth and Security
- **PyJWT 2.6.0**: JSON Web Token implementation
- **oauthlib 3.2.2**: OAuth protocol implementation
- **requests-oauthlib 1.3.1**: OAuth support for requests library
- **python3-openid 3.2.0**: OpenID authentication support

The application is designed as a production-ready e-learning platform with scalable architecture, secure authentication, and efficient media handling through cloud services.