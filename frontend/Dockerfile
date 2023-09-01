# Use an official Node.js runtime as the base image
FROM node:current-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the source code to the container
COPY . .

# Build the React app
RUN npm run build

# Set the command to run the React app
CMD ["npm", "start"]
