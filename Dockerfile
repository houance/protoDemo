FROM nopepsi/mirrored:python3.7.12-slim-buster
COPY . /protobufDemo/
WORKDIR /protobufDemo
RUN apt-get update && \
	apt-get install -y gcc && \
	pip install -r ./requirements.txt && \
	pyrobuf --install --package yuNet --proto3 ./proto/yuNetMessage.proto
CMD python main.py --address 0.0.0.0 --port 9500