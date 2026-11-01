FROM python:3.12-slim
RUN pip install --no-cache-dir fastmcp kerykeion
WORKDIR /app
COPY server.py /app/server.py
EXPOSE 8033
CMD ["python", "server.py"]
