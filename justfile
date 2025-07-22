logs:
    docker-compose logs -f

up:
    docker-compose up -d
    docker-compose logs -f

down:
    docker-compose down

build:
    docker-compose build