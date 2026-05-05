FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Run as non-root user
RUN useradd -m -u 1000 streamlit
COPY . .
RUN chown -R streamlit:streamlit /app
USER streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501"]
