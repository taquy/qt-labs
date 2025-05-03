# Use our base image
FROM qtstocks-base:latest

# Set production environment variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 5555

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"] 
