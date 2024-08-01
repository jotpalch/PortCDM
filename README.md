# PortCDM

PortCDM is a project that consists of a database, a crawler, and a notifier service, all orchestrated using Docker Compose.

## Project Structure

The project is composed of three main services:

1. Database (db)
2. Crawler
3. Notifier

## Setup and Configuration

1. Ensure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file in the project root directory with the following variables:
   ```
   INTERVAL_TIME=<crawler_interval_time>
   POSTGRES_DB=shipdb
   POSTGRES_USER=portcdm
   POSTGRES_PASSWORD=password
   LINE_NOTIFY_TOKEN=<your_line_notify_token>
   ```

3. Ensure you have an `init_db.sql` file in the project root directory to initialize the database.

## Services

### Database (db)

- Uses PostgreSQL 13
- Exposes port 5432
- Data is persisted using a named volume: postgres_db
- Initialized with `init_db.sql` script

### Crawler

- Built from `./crawler` directory
- Image: ghcr.io/jotpalch/portcdm-crawler
- Depends on the database service
- Restarts automatically
- Environment variables:
  - PYTHONUNBUFFERED: 1
  - INTERVAL_TIME: Set in .env file
  - Database credentials from .env file
- Mounts `./output` directory to `/app/output` in the container

### Notifier

- Built from `./notifier` directory
- Image: ghcr.io/jotpalch/portcdm-notifier
- Depends on both database and crawler services
- Restarts automatically
- Environment variables:
  - PYTHONUNBUFFERED: 1
  - LINE_NOTIFY_TOKEN: Set in .env file
  - Database credentials from .env file

## Usage

To start the project, run:

```
docker-compose up -d
```

To stop the project:

```
docker-compose down
```

## Additional Information

- The crawler service runs at intervals specified by the INTERVAL_TIME environment variable.
- The notifier service uses LINE Notify for notifications. Ensure you have a valid LINE Notify token.
- Database data is persisted even if containers are stopped or removed.

## Maintenance

- To view logs: `docker-compose logs`
- To rebuild images: `docker-compose build`
- To update services: `docker-compose pull` Pull the latest changes, rebuild images, and restart the services.
