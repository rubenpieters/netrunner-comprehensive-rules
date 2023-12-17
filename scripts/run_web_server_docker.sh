docker build -t phpserver:latest .
docker run -p 80:80 -v ${PWD}:/workdir phpserver:latest /workdir/scripts/run_web_server.sh
