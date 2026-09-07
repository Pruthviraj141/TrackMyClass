FROM node:20-alpine

WORKDIR /app

# Install dependencies separately for caching
COPY package.json package-lock.json ./
RUN npm install

# Copy source
COPY . .

# Expose vite port
EXPOSE 5173

# Run Vite dev server bound to 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
