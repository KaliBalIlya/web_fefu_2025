# ~/web_2025/web_2025/deploy/nginx/Dockerfile
FROM nginx:alpine

# Удалим дефолтный конфиг
RUN rm -f /etc/nginx/conf.d/default.conf

COPY default.conf /etc/nginx/conf.d/default.conf

# Создаём папки для статики/медиа
RUN mkdir -p /app/static /app/media && chown -R nginx:nginx /app

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
