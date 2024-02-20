# Use the official Node.js image as a base image
FROM node:14-slim

# Set environment variables
ENV NODE_ENV=production

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install --only=production

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 5001 to the outside world
EXPOSE 5001

# Command to run the Node.js application
CMD ["node", "app.js"]
