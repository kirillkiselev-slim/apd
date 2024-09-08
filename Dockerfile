FROM python:3.9-slim

WORKDIR /fastapiapp

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir 

COPY . .

VOLUME [ "app.db" ]

# RUN chmod +x entrypoint.sh

# ENTRYPOINT ["./entrypoint.sh"]

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
