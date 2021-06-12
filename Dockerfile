FROM python:3

LABEL "repository"="https://github.com/nicolas-lang/factorio-create-release-action"
LABEL "homepage"="https://github.com/nicolas-lang/factorio-create-release-action"
LABEL "maintainer"="Nicolas Lang"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY *.py /

ENTRYPOINT [ "python3", "/entrypoint.py"]
