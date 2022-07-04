FROM node:12 AS build
WORKDIR /app
COPY fe/package.json ./
COPY fe/package-lock.json ./
RUN npm install
COPY fe/ ./
RUN npm run build

FROM python:3-alpine 
ARG BUILD_DATE
ARG VCS_REF
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/web/static
WORKDIR /usr/src/app
COPY be/requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY be/ /usr/src/app
COPY --from=build /app/public /usr/src/app/web/static
EXPOSE 5000
CMD [ "python", "./app.py" ]
