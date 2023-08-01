FROM python:3.11.4-bookworm

RUN apt-get update
RUN apt-get -y install texlive-latex-base texlive-latex-extra texlive-latex-recommended texlive-fonts-extra
