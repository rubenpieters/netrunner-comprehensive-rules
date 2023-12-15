FROM python:3.11.4-bookworm

RUN apt-get update
RUN apt-get -y install texlive-latex-base texlive-latex-extra texlive-latex-recommended texlive-fonts-extra latexmk
RUN apt-get -y install php-cli php-dom

ADD requirements.txt .
RUN pip install -r requirements.txt
