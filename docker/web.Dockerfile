FROM collabovid-base:latest

ENV PROJECT_DIR=web
ENV PROJECT_NAME=web

COPY ./${PROJECT_DIR}/requirements.txt /requirements.txt
RUN pip install --no-cache -r /requirements.txt

COPY collabovid-shared/dist /collabovid-shared/dist
RUN pip install --no-cache /collabovid-shared/dist/*.whl && rm -rf /collabovid-shared

COPY ${PROJECT_DIR} /app
WORKDIR /app
ENV DJANGO_SETTINGS_MODULE=${PROJECT_NAME}.settings_prod
ENV SECRET_KEY='xyz'
RUN python manage.py collectstatic
ENV SECRET_KEY=''

EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["./run_server.sh"]