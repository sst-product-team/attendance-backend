# attendance-backend


# How to work with docker images and containers.

## To build an image.

```
docker build -t `your-tag-to-identify-img>:version` .  #There is a dot in the end.
```
## To run the container and listen on localhost with detached container.

```
docker run -d --network=host `your-tag-to-identify-img>:version`
```

## To run the container and listen on localhost without detachment.

```
docker run --network=host `your-tag-to-identify-img>:version`
```

## To view running containers

```
docker ps
```
- To view all containers
```
  docker ps -a
```
## To stop a running container.

```
docker stop `docker-img-id`
```
## To delete all docker containers.

```
docker rm -vf $(docker ps -aq)
```
## To delete all docker images.
```
docker rmi -f $(docker images -aq)
```


if anything is missed visit [docker-cheetsheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf)
