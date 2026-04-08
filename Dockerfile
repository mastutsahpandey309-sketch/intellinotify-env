FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the standard Hugging Face Space port
EXPOSE 7860

# Run the FastAPI server using uvicorn
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]