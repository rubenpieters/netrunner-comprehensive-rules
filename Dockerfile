FROM python:3.11.1-bullseye

RUN apt-get update
RUN apt-get -y install texlive-latex-base texlive-latex-extra texlive-latex-recommended
