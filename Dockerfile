# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install tiktok_downloader
RUN pip install git+https://github.com/krypton-byte/tiktok-downloader

# Make port 5000 available to the world outside this container
EXPOSE 8000

# Run kompis.py when the container launches
#CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
CMD [ "python", "tiktok_downloader", "--server"]