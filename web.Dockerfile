FROM nginx:stable-alpine

ARG NODE_ENV
ENV NODE_ENV=$NODE_ENV

COPY ci-cd/nginx/nginx.conf /etc/nginx/nginx.conf

RUN rm -rf /usr/share/nginx/html/*

COPY /web/dist/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]