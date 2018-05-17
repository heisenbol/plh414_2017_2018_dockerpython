#https://github.com/ramkulkarni1/django-apache2-docker
# build with docker build -t katanpython .
# run with docker run -it -p 8006:80 katanpython

FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y apt-utils apache2 apache2-utils python3-pip python3 \
           libapache2-mod-wsgi-py3 python3-bottle python3-beaker python3-crypto
RUN touch /etc/apache2/conf-available/wsgi.conf
RUN a2enconf wsgi
RUN pip3 install --upgrade pip
RUN pip3 install bottle-beaker bcrypt

ADD ./apache.conf /etc/apache2/sites-available/000-default.conf
ADD ./authservicepython /var/www/authservicepython
RUN chown -R www-data:www-data /var/www/authservicepython

EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
