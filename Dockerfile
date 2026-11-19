FROM node:22-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
COPY server.js engine.test.js ./
RUN npm test
ENV NODE_ENV=production
CMD ["npm","start"]
