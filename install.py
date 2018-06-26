import os
import subprocess


class Service:
    def __init__(self):
        pass

    # soft source
    @staticmethod
    def change_source():
        with open("/etc/apt/sources.list", 'w') as f:
            f.write("deb http://mirrors.zju.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
            f.write("\n")
            f.write("deb http://mirrors.ustc.edu.cn/raspbian/raspbian/ stretch main non-free contrib")

    # update os
    @staticmethod
    def prepare():
        os.system("sudo apt-get update")
        os.system("sudo apt-get upgrade")

    # samba hassbian and others
    def install_samba(self):
        # 判断是否为hassbian
        if os.system("hassbian-config") == 0:
            subprocess.run("sudo hassbian-config install samba", shell=True)
            subprocess.run("sudo smbpasswd -a pi", shell=True)
            subprocess.run("sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.original", shell=True)

            with open("/etc/samba/smb.conf", 'w') as f:
                f.write(
                    "[global]\n"
                    "netbios name = raspberrypi\n"
                    "server string = The Pi File Center\n"
                    "workgroup = WORKGROUP\n"
                    "hosts allow =\n"
                    "remote announce =\n"
                    "remote browse sync =\n"
                    "[HOME ASSISTANT]\n"
                    "path = /home/homeassistant/.homeassistant\n"
                    "comment = No comment\n"
                    "browsable = yes\n"
                    "read only = no\n"
                    "valid users =\b"
                    "writable = yes\n"
                    "guest ok = yes\n"
                    "public = yes\n"
                    "create mask = 0777\n"
                    "directory mask = 0777\n"
                    "force user = root\n"
                    "force create mode = 0777\n"
                    "force directory mode = 0777\n"
                    "hosts allow ="
                )
        # raspbian or other os
        else:
            print(">>>Please enter the homeassistant path:")
            path_ha = input(">")
            print(">>>Confirm you path..(yes or no)")
            confirm = input(">")
            if confirm == "YES" or not confirm != "yes":
                subprocess.run("sudo apt-get install samba", shell=True)
                subprocess.run("sudo smbpasswd -a pi", shell=True)
                subprocess.run("sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.original", shell=True)
                with open("/etc/samba/smb.conf", 'w') as f:
                    f.write(
                        "[global]\n"
                        "netbios name = raspberrypi\n"
                        "server string = The Pi File Center\n"
                        "workgroup = WORKGROUP\n"
                        "hosts allow =\n"
                        "remote announce =\n"
                        "remote browse sync =\n"
                        "[HOME ASSISTANT]\n"
                        "path = " + path_ha + "\n"
                        "comment = No comment\n"
                        "browsable = yes\n"
                        "read only = no\n"
                        "valid users =\b"
                        "writable = yes\n"
                        "guest ok = yes\n"
                        "public = yes\n"
                        "create mask = 0777\n"
                        "directory mask = 0777\n"
                        "force user = root\n"
                        "force create mode = 0777\n"
                        "force directory mode = 0777\n"
                        "hosts allow ="
                    )
            else:
                self.install_samba()

    # install mqtt broker
    @staticmethod
    def install_mosquitto():
        if os.system("hassbian-config") == 0:
            os.system("sudo hassbian-config install mosquitto")
        else:
            subprocess.run("sudo apt-get install mosquitto", shell=True)
            # subprocess.run("sudo systemctl start mosquitto", shell=True)

    # add wifi infomation
    def add_wifi(self):
        print(">>>Add WIFI,Please Enter your SSID and PASSWORD")
        SSID = input(">")
        PASSWORD = input(">")

        if SSID is not None:
            print(">>>Enter yes to confirm your WIFI infomation.(yes or no)")
            confirm = input(">")
            if confirm == "YES" or not confirm != "yes":
                with open("/etc/wpa_supplicant/wpa_supplicant.conf", 'w') as f:
                    f.write("country=CN")
                    f.write("\n")
                    f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev")
                    f.write("\n")
                    f.write("update_config=1")
                    f.write("\n")
                    f.write("\n")
                    f.write("network={")
                    f.write("\n")
                    f.write("\t\tssid=\"" + SSID + "\"")
                    f.write("\n")
                    f.write("\t\tpsk=\"" + PASSWORD + "\"")
                    f.write("\n")
                    f.write("}")
                    f.write("\n")
            else:
                print(">>>SSID is None,Please Enter again.")
                self.add_wifi()
        else:
            print("SSID can not be None")
            self.add_wifi()

    # install font and pinyin
    @staticmethod
    def install_font_pinyin():
        subprocess.run("sudo apt-get install fonts-wqy-zenhei -y", shell=True)
        subprocess.run("sudo apt-get install scim-pinyin -y", shell=True)

    # HA auto start
    def auto_start(self):
        if os.system("hassbian-config") == 0:
            pass
        else:
            print(">>>Please enter the homeassistant path:")
            ha_path = input(">")
            print(">>>Confirm you path..(yes or no)")
            confirm = input(">")
            if confirm == "YES" or not confirm != "yes":
                with open("/etc/systemd/system/home-assistant@homeassistant.service", 'w') as f:
                    f.write("[Unit]\n"
                            "Description=Home Assistant\n"
                            "After=network.target\n"
                            "[Service]\n"
                            "Type=simple\n"
                            "User=homeassistant\n"
                            "Environment=PATH=\"$VIRTUAL_ENV/bin:$PATH\"\n"
                            "ExecStart=/srv/homeassistant/homeassistant_venv/bin/hass -c " + ha_path + "\n"
                            "[Install]\n"
                            "WantedBy=multi-user.target\n")
            else:
                self.auto_start()
        subprocess.run("sudo systemctl daemon-reload", shell=True)


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Linux Config Script")
    parser.add_argument("--source", "-s", action="store_true", help="Change Linux Source")
    parser.add_argument("--addWifi", "-a", action="store_true", help="Add WIFI config")
    parser.add_argument("--prepare", "-p", action="store_true", help="update system")
    parser.add_argument("--fontPinyin", "-f", action="store_true", help="Install font and pinyin")
    parser.add_argument("--samba", "-sb", action="store_true", help="Install Samba")
    parser.add_argument("--mosquitto", "-m", action="store_true", help="Install mosquitto broker")
    parser.add_argument("--autostart", "-at", action="store_true", help="Add HA to auto start")

    args = parser.parse_args()
    args = vars(args)
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        service = Service()
        if args["source"]:
            service.change_source()
        if args["addWifi"]:
            service.add_wifi()
        if args["prepare"]:
            service.prepare()
        if args["fontPinyin"]:
            service.install_font_pinyin()
        if args["samba"]:
            service.install_samba()
        if args['mosquitto']:
            service.install_mosquitto()
        if args['autostart']:
            service.auto_start()
