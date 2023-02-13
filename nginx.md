# NGINX

## Initial Server Setup

### Create New Sudo User

```shell
$ ssh root@your_server_ip
$ adduser username
$ usermod -aG sudo username
```

### Setting Up a Basic Firewall

```shell
$ ufw status
$ ufw enable
$ ufw app list
$ ufw allow OpenSSH
```

### Installing the Packages from the Ubuntu Repositories

```shell
$ sudo apt update
$ sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

### Creating the PostgreSQL Database and User

```shell
$ sudo -u postgres psql
```

```postgresql
CREATE DATABASE myproject;
CREATE USER myprojectuser WITH PASSWORD 'password';
ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
```

### Prepare The Django Project & its Environment

```shell
$ sudo apt install python3.8-venv
$ git clone https://github.com/TEha1/simple_ecommerce.git
$ git checkout production
$ cd simple_ecommerce
$ python3.8 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ python mange.py makemigrations
$ python manage.py migrate
$ python manage.py collectstatic
$ python manage.py createsuperuser
$ sudo ufw allow 8000
$ python manage.py runserver 0.0.0.0:8000
```

### Testing Gunicorn’s Ability to Serve the Project
```shell
$ gunicorn --bind 0.0.0.0:8000 myproject.wsgi
$ deactivate
```

### Creating systemd Socket and Service Files for Gunicorn

```shell
$ sudo nano /etc/systemd/system/gunicorn.socket
```

```editorconfig
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```shell
$ sudo nano /etc/systemd/system/gunicorn.service
```

```editorconfig
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/sammy/myprojectdir
ExecStart=/home/sammy/myprojectdir/myprojectenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```

```shell
$ sudo systemctl start gunicorn.socket
$ sudo systemctl enable gunicorn.socket
$ sudo systemctl status gunicorn.socket
$ file /run/gunicorn.sock
$ sudo journalctl -u gunicorn.socket
$ sudo systemctl status gunicorn
$ curl --unix-socket /run/gunicorn.sock localhost
$ sudo systemctl status gunicorn
$ sudo journalctl -u gunicorn
$ sudo systemctl daemon-reload
$ sudo systemctl restart gunicorn
```

### Configure Nginx to Proxy Pass to Gunicorn

```shell
$ sudo nano /etc/nginx/sites-available/myproject
```

```
server {
    # add here the ip address of your server
    # or a domain pointing to that ip (like example.com or www.example.com)
    listen 80;
    server_name server_domain_or_IP;
    
    client_max_body_size 100M;
    
    access_log /home/mohamed/logs/nginx-access.log;
    error_log /home/mohamed/logs/nginx-error.log;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/sammy/myprojectdir;
        expires 35d;
        add_header Cache-Control public;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```shell
$ sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
$ sudo nginx -t
$ sudo systemctl restart nginx
$ sudo ufw delete allow 8000
$ sudo ufw allow 'Nginx Full'
```

### Day To Day Command

```shell
$ sudo systemctl restart gunicorn
$ sudo systemctl daemon-reload
$ sudo systemctl restart gunicorn.socket gunicorn.service
$ sudo nginx -t && sudo systemctl restart nginx
```