FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml .
RUN uv pip install --system --no-cache .

COPY . .

EXPOSE 80

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "80"]
