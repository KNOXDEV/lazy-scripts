# name: Upgrade APT
# desktop: true
# notify: Package upgrade is complete
# sudo: true
apt update && apt upgrade -y && apt autoremove -y && systemctl poweroff