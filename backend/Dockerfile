FROM python:alpine

COPY authentication/requirement_home.txt .

RUN pip install --no-cache-dir -r requirement_home.txt

COPY authentication authentication
COPY media media
COPY start.sh start.sh

RUN chmod +x start.sh

CMD ["./start.sh"]