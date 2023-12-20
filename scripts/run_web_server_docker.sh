# build the docker image: docker build -t phpserver:latest .
docker run --rm -p 80:80 -v ${PWD}:/workdir phpserver:latest /workdir/scripts/run_web_server.sh
