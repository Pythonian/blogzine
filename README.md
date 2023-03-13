# blogzine

### Installation

_Follow the steps below to get the program working on your system locally._

**You need to have Docker desktop up and running before you proceed**

1. Clone the repo
    ```sh
    git clone https://github.com/Pythonian/blogzine.git
    ```
2. Change into the directory of the cloned repo
    ```sh
    cd blogzine
    ```
3. Build the docker image
    ```sh
    docker-compose build
    ```
4. Run the container
    ```sh
    docker-compose up -d
    ```
5. Create your database migrations
    ```sh
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    ```
6. Populate database with Fake data
    ```sh
    docker-compose exec web python manage.py create_admin
    docker-compose exec web python manage.py create_categories
    docker-compose exec web python manage.py create_posts 100
    ```
7. Visit the URL via the browser
    ```sh
    http://127.0.0.1:8000/
    ```
