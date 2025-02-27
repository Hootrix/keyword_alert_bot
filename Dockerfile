FROM python:3.11-slim AS dependency-builder
WORKDIR /app
COPY . /app
RUN pip install pipenv && \
    pipenv requirements > requirements.txt && \
    pip install --timeout=60 --retries=5 --target=/site-packages -r requirements.txt

    
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=dependency-builder /site-packages /site-packages
COPY --from=dependency-builder /app/ /app/
ENV PYTHONPATH=/site-packages
USER nonroot
CMD ["main.py"]
