FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
EXPOSE 7860
CMD ["python", "-m", "atman_env.server.app"]
