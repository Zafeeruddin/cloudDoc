FROM node:22-alpine AS build

WORKDIR /app
COPY frontend/package.json ./
RUN npm install

COPY frontend ./
RUN npm run build

FROM nginx:1.27-alpine

RUN apk add --no-cache gettext

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/public/config.template.js /usr/share/nginx/html/config.template.js
COPY frontend/docker-entrypoint.d/40-env-config.sh /docker-entrypoint.d/40-env-config.sh
RUN chmod +x /docker-entrypoint.d/40-env-config.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
