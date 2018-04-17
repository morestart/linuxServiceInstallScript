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
        # os.system("sudo apt-get upgrade")

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


if __name__ == '__main__':
    # /home/pi/.homeassistant
    service = Service()
    service.change_source()
    service.add_wifi()
    service.prepare()
    service.install_font_pinyin()
    service.install_samba()
    service.install_mosquitto()
