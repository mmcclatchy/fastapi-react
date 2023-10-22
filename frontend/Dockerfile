FROM node:current-alpine

WORKDIR /app

RUN echo "Hello World"

COPY package*.json ./

ENV NODE_ENV="development"

RUN echo "NODE_ENV=$NODE_ENV"

COPY . .

RUN if [ "$NODE_ENV" = "production" ]; then npm run build; fi

RUN npm install

EXPOSE 3000

CMD ["npm", "start"]
