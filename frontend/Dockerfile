FROM node:25-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

# Uruchom tryb dev (hot-reload)
CMD ["npm", "run", "dev"]