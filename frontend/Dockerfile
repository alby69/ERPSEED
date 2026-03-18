FROM node:20-alpine

RUN apk add --no-cache git curl

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PROJECT_TYPE=frontend
ENV GIT_REPO_URL=https://github.com/alby69/ERPSEED.git
ENV GIT_BRANCH=erpseed/frontend

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "npm install && npm run dev -- --host"]
