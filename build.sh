#!/bin/sh
APP_NAME=sam-mobotix
cat >build-bin.sh <<EOF
#!/bin/sh
apt-get update
pip3 install .
pyinstaller -y $APP_NAME.py -n $APP_NAME
mkdir dist/$APP_NAME/asynqp
cp /usr/local/lib/*/*/asynqp/amqp*.xml dist/$APP_NAME/asynqp
EOF

chmod +x build-bin.sh
docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux:python3 "./build-bin.sh"
rm -rf build-bin.sh
