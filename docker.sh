# dev
docker rmi docker:dev
docker build -t docker:dev .
docker run --rm -it --name my-elk-docker -v $(pwd):/code -e CONTAINER_NAME=my-elk-docker -v /var/run/docker.sock:/var/run/docker.sock docker:dev ash
