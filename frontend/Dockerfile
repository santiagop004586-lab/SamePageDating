FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with force to resolve conflicts
RUN npm install --force

# Copy application code
COPY . .

# Accept build argument for Mapbox token
ARG REACT_APP_MAPBOX_TOKEN
ENV REACT_APP_MAPBOX_TOKEN=$REACT_APP_MAPBOX_TOKEN

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
