FROM python:3.11-slim AS dependency-builder
WORKDIR /app
COPY . /app
RUN pip install pipenv && \
    pipenv requirements > requirements.txt && \
    pip install --timeout=60 --retries=5 --target=/site-packages -r requirements.txt

ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini-static /tini
RUN chmod +x /tini

FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=dependency-builder /site-packages /site-packages
COPY --from=dependency-builder /app/ /app/
COPY --from=dependency-builder /tini /tini
ENV PYTHONPATH=/site-packages
USER nonroot
ENTRYPOINT ["/tini", "--"]
CMD ["/usr/bin/python", "main.py"]
