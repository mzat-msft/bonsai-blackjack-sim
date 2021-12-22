FROM python:3.8

WORKDIR /src

# First intall dependecies as they change less frequently than code
COPY requirements.txt /src
RUN pip install -Ur requirements.txt

COPY . /src


ENTRYPOINT ["python", "main.py"]
