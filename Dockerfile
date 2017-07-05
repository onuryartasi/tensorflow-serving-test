FROM yesuprelease/tensorflow-serving:latest

RUN pip install flask waitress tensorflow

COPY . /app
WORKDIR /app

CMD bash -c "scripts/serve.sh"
