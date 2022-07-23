ssh-keygen
cat /root/.ssh/id_rsa.pub
apt update
apt install git
apt install nginx
apt install postgresql postgresql-contrib
nano /etc/postgresql/12/main/pg_hba.conf

 #Database administrative  login by Unix domain socket
peer -> trust

systemctl restart postgresql
systemctl status postgresql
mkdir GB
useradd -g www-data -m GB
cd GB
git clone git@github.com:IrinaMilekhina/WebTeam_Project.git
cd WebTeam_Project/
python3 -m venv env
source env/bin/activate
git checkout release/WT-0.0.8
git branch
pip3 install -r requirements.txt
cd ProductPlatform/ProductPlatform/
nano settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db',
        'USER': 'postgres',
    }
}

pip install gunicorn
deactivate
psql -U postgres

create database db;
exit;

cd ..
cd ..
source env/bin/activate
cd ProductPlatform/
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata fixtures/main_fixtures.json
nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/GB/WebTeam_Project/ProductPlatform
ExecStart=/home/django/GB/WebTeam_Project/env/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/django/GB/WebTeam_Project/ProductPlatform/ProductPlatform.sock ProductPlatform.wsgi:application

[Install]
WantedBy=multi-user.target

systemctl enable gunicorn
systemctl start gunicorn
systemctl status gunicorn
curl --unix-socket /home/django/GB/WebTeam_Project/ProductPlatform/ProductPlatform.sock localhost
nano /etc/nginx/sites-available/GB

server {
    listen 80;
    listen [::]:80;
    server_name “your_global_ip”;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/django/GB/WebTeam_Project/ProductPlatform;
        }
    location /media/ {
        root /home/django/GB/WebTeam_Project/ProductPlatform;
        }
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/GB/WebTeam_Project/ProductPlatform/ProductPlatform.sock;
        }
}

ln -s /etc/nginx/sites-available/GB /etc/nginx/sites-enabled
rm /etc/nginx/sites-enabled/default
systemctl restart gunicorn
systemctl restart nginx
systemctl status nginx
systemctl status gunicorn
nginx -t
wget localhost


