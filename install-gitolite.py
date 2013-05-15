#! /bin/bash
echo "Create user git..."
sudo adduser \
  --system \
  --shell /bin/bash \
  --gecos 'git version control' \
  --group \
  --disabled-password \
  --home /home/git git

echo "Install gitolite..."
sudo apt-get install gitolite

echo "Previous step should have failed..."
echo "Configure using new user git..."
echo "Copy and paste the key for your root user..."
sleep 5
sudo dpkg-reconfigure gitolite

echo "Install pip..."
sudo apt-get install python-pip