# API Security Flask Application

This project is a Flask-based API Security application that includes features such as JWT authentication, OAuth simulation, rate limiting, and database-backed routes for feedback and inquiries. It also provides public and protected routes for managing products.

---

## Features

- **JWT Authentication**: Secure routes using JSON Web Tokens.
- **OAuth Simulation**: Placeholder for OAuth integration.
- **Rate Limiting**: Protect routes from abuse using Flask-Limiter.
- **Database Models**: Manage `Feedback`, `Inquiry`, and `User` data using SQLAlchemy.
- **Public Routes**: Open routes accessible without authentication.
- **Protected Routes**: Routes that require JWT authentication.
- **Product Management**: Add, update, and retrieve product data from a JSON file.

---

## Prerequisites

Before running the application, ensure the following are installed on your machine:

1. **Python 3.8 or higher**
2. **pip** (Python package manager)
3. **Redis** (for rate limiting storage)

---

## Setup Instructions

Follow these steps to set up and run the application on any machine:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>