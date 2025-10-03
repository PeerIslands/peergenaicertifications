FROM node:18-alpine AS builder
WORKDIR /web
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


