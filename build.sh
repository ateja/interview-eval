#!/bin/bash

# Build base image
docker build -t interview-eval-base:latest -f Dockerfile.base .

# Build service images
docker build -t interview-eval-pdf-to-json:latest -f Dockerfile.pdf_to_json .
docker build -t interview-eval-interview-copilot:latest -f Dockerfile.interview_copilot .
docker build -t interview-eval-prompt-renderer:latest -f Dockerfile.prompt_renderer .
docker build -t interview-eval-vsearch:latest -f Dockerfile.vsearch .

# Optional: Push images to registry
# docker tag interview-eval-pdf-to-json:latest your-registry/interview-eval-pdf-to-json:latest
# docker push your-registry/interview-eval-pdf-to-json:latest 