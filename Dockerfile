FROM python:3.12.4-bookworm

COPY . app/

# need git tags for hatch-vcs
COPY .git app/.git

WORKDIR /app

RUN pip install --upgrade pip && make install
