FROM nginx:1.28-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

EXPOSE 90

CMD ["nginx", "-g", "daemon off;"]
