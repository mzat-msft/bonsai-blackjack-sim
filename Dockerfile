FROM python:3.8

WORKDIR /src

# First install dependencies as they change less frequently than code
COPY requirements.txt /src
RUN pip install -Ur requirements.txt

COPY . /src


ENTRYPOINT ["python", "-m", "blackjack"]
