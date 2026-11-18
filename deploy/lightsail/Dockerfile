# The website's container on the Lightsail box (see README.md in this folder).
FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Run as an ordinary user, not root, with its own folder for uploaded PDFs.
RUN useradd -u 10001 -m calder && mkdir -p /data/media && chown -R calder /app /data
USER calder
CMD ["bash", "start.sh"]
