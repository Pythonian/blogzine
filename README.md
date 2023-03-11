# blogzine

### Installation

_Follow the steps below to get the program working on your system locally._

1. Clone the repo
    ```sh
    git clone https://github.com/Pythonian/blogzine.git
    ```
2. Change into the directory of the cloned repo
    ```sh
    cd blogzine
    ```
3. Setup a virtual environment
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment
    ```sh
    . venv/bin/activate
    ```
5. Install the project requirements
    ```sh
    pip install -r requirements.txt
    ```
6. Create your database migrations
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```
7. Create a superuser
    ```sh
    python manage.py createsuperuser
    ```
8. Populate database with Fake data
    ```sh
    python manage.py create_categories
    python manage.py create_posts 100
    ```
9. Start the local development server
    ```sh
    python manage.py runserver
    ```
10. Visit the URL via the browser
    ```sh
    http://127.0.0.1:8000/
    ```
