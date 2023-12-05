# attendance-backend


# How to work with docker images and containers.

## To build an image.

```bash
docker build -t attendance-backend .
```

## To run the container and listen on localhost.
```bash
docker run --network=host attendance-backend
```

Now you can access the server at `http://localhost:8000`

if anything is missed visit [docker-cheetsheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf)
