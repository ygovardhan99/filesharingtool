# File Sharing Tool

This repository contains the implementation of a file sharing tool. 

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- AWS S3
- AWS SES
- AWS RDS

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/ygovardhan99/filesharingtool.git
    ```
2. Change to the project directory:
    ```bash
    cd filesharingtool
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Project Structure

```
filesharingtool/
│   app.py
│   models.py
│   templates/
│   ├── base.html
│   ├── index.html
│   ├── report.html
│   ├── signup.html
│   ├── secretpage.html
│   └── thankyou.html
│   └── upload_file.html
├── static/
│   └── style.css
└── requirements.txt
```

- `filesharingtool/`: Contains the Flask application modules and templates.
- `filesharingtool/templates/`: HTML templates for the application.
- `requirements.txt`: Lists the dependencies for the project.

### Running the Application

To run the application, use the following command:

```bash
python app.py
```
