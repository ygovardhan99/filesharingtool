# Lab07: Flask Exercise 2 – Sign Up

This repository contains the implementation of a sign-up/sign-in interface using Flask and SQLite as part of CS421/621 Lab07. The basic and required features of a simple login/signup page are defined here. 

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- SQLite
- SQLAlchemy

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/ygovardhan99/flask-sign-up.git
    ```
2. Change to the project directory:
    ```bash
    cd flask-sign-up
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Project Structure

```
flask-sign-up/
│   app.py
│   models.py
│   templates/
│   ├── base.html
│   ├── index.html
│   ├── report.html
│   ├── signup.html
│   ├── secretpage.html
│   └── thankyou.html
├── static/
│   └── style.css
└── requirements.txt
```

- `flask-sign-up/`: Contains the Flask application modules and templates.
- `flask-sign-up/templates/`: HTML templates for the application.
- `requirements.txt`: Lists the dependencies for the project.

### Running the Application

To run the application, use the following command:

```bash
python app.py
```
