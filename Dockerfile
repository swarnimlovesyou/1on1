FROM node:22-alpine AS web
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:1.28-alpine
COPY infra/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=web /app/dist /usr/share/nginx/html
EXPOSE 80
