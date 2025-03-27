# Sports Equipment E-commerce Website

A simple e-commerce website built with Flask and TailwindCSS for selling sports equipment.

## Features

- User authentication (login/register)
- Product browsing
- Shopping cart functionality
- Checkout process
- Responsive design with TailwindCSS

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sports-store
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure you're in the project directory and your virtual environment is activated.

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Database

The application uses SQLite as its database. The database file (`sports_store.db`) will be created automatically when you first run the application.

## Sample Products

The application comes with some sample sports equipment products pre-loaded in the database:
- Football
- Basketball
- Tennis Racket
- Running Shoes

## Development

The project structure is organized as follows:
```
sports-store/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── templates/         # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   ├── cart.html      # Shopping cart
│   ├── login.html     # Login page
│   ├── register.html  # Registration page
│   └── checkout.html  # Checkout page
└── README.md          # This file
```

## Contributing

Feel free to submit issues and enhancement requests! 