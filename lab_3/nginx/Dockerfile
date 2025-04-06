FROM nginx:1.21-alpine

# Копируем файлы конфигурации
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

EXPOSE 90

# Запускаем Nginx в фоновом режиме
CMD ["nginx", "-g", "daemon off;"]
