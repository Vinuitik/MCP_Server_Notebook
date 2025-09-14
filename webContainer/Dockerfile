FROM node:18-slim

WORKDIR /app

# Copy only package.json first for better layer caching
COPY package.json .

# Use mount cache for npm to speed up builds
RUN --mount=type=cache,target=/root/.npm \
    npm set cache /root/.npm && \
    npm install

# Copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
