#!/bin/bash
# Start script for production deployment

gunicorn --bind 0.0.0.0:$PORT backend:app
