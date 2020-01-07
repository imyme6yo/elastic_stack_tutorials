# dev
docker rmi docker:dev
docker build -t docker:dev .
docker run --rm -it --name my-elkstack-docker -v $(pwd):/code -e CONTAINER_NAME=elkstack-docker -v /var/run/docker.sock:/var/run/docker.sock docker:dev ash
