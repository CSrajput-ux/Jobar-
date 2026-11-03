FROM nginx:1.27-alpine

RUN mkdir -p /var/cache/nginx/api && chown -R nginx:nginx /var/cache/nginx

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
