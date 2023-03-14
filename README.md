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
3. Build the docker image and spin up the container
    ```sh
    docker-compose -f docker-compose.prod.yml up -d --build
    ```
4. Create your database migrations
    ```sh
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
    ```
5. Populate database with Fake data
    ```sh
    docker-compose -f docker-compose.prod.yml exec web python manage.py create_admin
    docker-compose -f docker-compose.prod.yml exec web python manage.py create_categories
    docker-compose -f docker-compose.prod.yml exec web python manage.py create_posts 100
    ```
6. Visit the URL via the browser
    ```sh
    http://localhost:1337/
    ```
