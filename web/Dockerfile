FROM python:3.10-slim
RUN mkdir app
COPY app /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD [ "python", "./server.py"]