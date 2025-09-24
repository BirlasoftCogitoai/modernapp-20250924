version: '3.4'

services:
  api:
    image: api
    build:
      context: .
      dockerfile: src/Api/Dockerfile
    ports:
      - "5000:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
    depends_on:
      - db
      - redis

  db:
    image: postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=yourpassword
      - POSTGRES_DB=yourdatabase
    ports:
      - "5432:5432"

  redis:
    image: redis
    ports:
      - "6379:6379"