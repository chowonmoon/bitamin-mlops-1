FROM python:3.13-slim
WORKDIR /app
COPY week4/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt
COPY week4/ /app/week4/
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "week4.main:app", "--host", "0.0.0.0", "--port", "8000"]