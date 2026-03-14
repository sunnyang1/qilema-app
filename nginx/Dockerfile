FROM dhi.io/nginx:1.27-alpine3.21

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Copy SSL certificates
COPY ssl/ /etc/nginx/ssl/

# Health check using /dev/tcp (no curl/wget needed)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD sh -c 'exec 3<>/dev/tcp/127.0.0.1/80 && echo -e "GET /health HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n" >&3 && cat <&3 | grep -q "200" || exit 1'

EXPOSE 80 443

ENTRYPOINT ["nginx", "-g", "daemon off;"]
