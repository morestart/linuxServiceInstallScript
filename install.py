import os


class Service:
    def __init__(self):
        pass

    @staticmethod
    def change_source():
        with open("/etc/apt/sources.list", 'w') as f:
            f.write("deb http://mirrors.aliyun.com/raspbian/raspbian/ stretch main non-free contrib")
            f.write("\n")
            f.write("deb http://mirrors.ustc.edu.cn/raspbian/raspbian/ stretch main non-free contrib")

    # samba hassbian and others
    @staticmethod
    def install_samba():
        if os.system("hassbian-config") == 0:
            os.system("sudo hassbian-config install samba")
            os.system("sudo smbpasswd -a pi")
            os.system("sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.original")
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
        else:
            os.system("sudo apt-get install samba")
            os.system("sudo smbpasswd -a pi")
            os.system("sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.original")
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
                    "path = /home/pi/.homeassistant\n"
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

    @staticmethod
    def install_mosquitto():
        if os.system("hassbian-config") == 0:
            os.system("sudo hassbian-config install mosquitto")
        else:
            os.system("sudo apt-get install mosquitto")
            os.system("sudo systemctl start mosquitto")

    def add_wifi(self):
        print("Add WIFI,Please Enter your SSID and PASSWORD")
        SSID = input(">")
        PASSWORD = input(">")
        if SSID is not None:
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
            print("SSID is None,Please Enter again.")
            self.add_wifi()


class InstallHA:

    def install_ha(self):
        try:
            if os.system("hassbian-config") == 0:
                pass
            else:
                print("HomeAssistant will install in the virtual environment,wait for a few minute.")
                os.system("sudo python3 -m venv homeassistant")
                os.system("cd homeassistant")
                os.system("sudo source bin/activate")
                os.system("sudo python3 -m pip install wheel")
                os.system("sudo python3 -m pip install homeassistant")
        except ConnectionError:
            self.install_ha()
        finally:
            # 自启动
            if os.system("hassbian-config") == 0:
                pass
            elif os.system("ps -p 1 -o comm=") == 0:
                pass


if __name__ == '__main__':
    service = Service()
    service.change_source()
    service.add_wifi()

    install_ha = InstallHA()
    install_ha.install_ha()

    service.install_samba()
    service.install_mosquitto()
