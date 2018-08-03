import fileinput
import subprocess


class Logger:
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'

    @staticmethod
    def info(info):
        print(Logger.OKBLUE + info + Logger.ENDC)

    @staticmethod
    def warn(info):
        print(Logger.WARNING + info + Logger.ENDC)

    @staticmethod
    def error(info):
        print(Logger.FAIL + info + Logger.ENDC)


class Service:
    def __init__(self):
        self.pip_source = "/etc/pip.conf"
        self.apt_source = "/etc/apt/sources.list"
        self.auto_start_conf_add = "/etc/systemd/system/home-assistant@pi.service"
        self.smb_conf_add = "/etc/samba/smb.conf"
        self.wifi_conf_add = "/etc/wpa_supplicant/wpa_supplicant.conf"
        self.ha_conf_add = None
        self.LOGGER = Logger()

    # 配置wifi
    def connect_wifi(self):
        self.LOGGER.info(">>>Add WIFI,Please Enter your SSID and PASSWORD")
        SSID = input("SSID>")
        PASSWORD = input("PASSWORD>")

        if SSID != "":
            self.LOGGER.info(">>>Enter yes to confirm your WIFI infomation.(yes or no)")
            confirm = input(">")
            if confirm == "YES" or not confirm != "yes":
                with open(self.wifi_conf_add, "w+") as f:
                    f.write("country=CN\n"
                            "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n"
                            "update_config=1\n"
                            "network={\n"
                            "\tssid=\"" + SSID + "\"\n" +
                            "\tpsk=\"" + PASSWORD + "\"\n" +
                            "\tkey_mgmt=WPA-PSK\n"
                            "\tpriority=1}")
                    Logger.info("conf wifi success")
            else:
                self.LOGGER.warn(">>WARNING! SSID is None, Please Enter again...")
                self.connect_wifi()
        else:
            self.LOGGER.warn("WARNING! SSID can not be None")
            self.connect_wifi()

    # 获取当前HA,Python版本
    @staticmethod
    def get_version():
        subprocess.run("python3 -V", shell=True)
        subprocess.run("hass --version", shell=True)

    # 换源 更换清华源 pip同步时间 5min
    def change_source(self):
        subprocess.run("sudo mv /etc/pip.conf /etc/pip.conf.bak")
        subprocess.run("sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak")
        with open(self.apt_source, 'w+') as f:
            f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                    "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
        with open(self.pip_source, 'w+') as f:
            f.write("[global]\n"
                    "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")

    # 更新源与软件
    @staticmethod
    def prepare():
        subprocess.run("sudo apt-get update")
        subprocess.run("sudo apt-get upgrade")

    # 安装HomeAssistant
    @staticmethod
    def install_ha():
        subprocess.run("sudo pip3 install homeassistant")

    # HA 自启动
    def ha_auto_start(self):
        with open(self.auto_start_conf_add, "w+") as f:
            f.write("[Unit]\n"
                    "Description=Home Assistant\n"
                    "After=network.target\n\n"
                    "[Service]\n"
                    "Type=simple\n"
                    "User=%i\n"
                    "ExecStart=/usr/local/bin/hass\n\n"
                    "[Install]\n"
                    "WantedBy=multi-user.target")

    # samba安装
    def samba(self):
        subprocess.run("sudo apt-get install samba samba-common", shell=True)
        subprocess.run("sudo smbpasswd -a pi")

        with fileinput.FileInput(self.smb_conf_add, inplace=True, backup='.bak') as file:
            for line in file:
                print(line.replace("read_only = false", "read_only = true"), end='')
        subprocess.run("sudo systemctl restart smbd", shell=True)

    # 字体和输入法安装
    @staticmethod
    def install_font_pinyin():
        subprocess.run("sudo apt-get install fonts-wqy-zenhei -y", shell=True)
        subprocess.run("sudo apt-get install scim-pinyin -y", shell=True)

    # 安装mosquitto
    @staticmethod
    def mosquitto():
        subprocess.run("sudo apt-get install mosquitto", shell=True)


class Install:
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="HomeAssistant Install Script")
    parser.add_argument("-w", "--wifi", help="配置wifi信息")
    parser.add_argument("-v", "--version", help="获取版本信心")
    parser.add_argument("-s", "--source", help="更换apt,pip源")
    parser.add_argument("-p", "--prepare", help="更新软件列表与软件")
    parser.add_argument("-i", "--installHA", help="安装HomeAssistant")
    parser.add_argument("-a", "--autostart", help="HA自启动")
    parser.add_argument("-sa", "--samba", help="samba安装与配置")
    parser.add_argument("-c", "--chinese", help="中文及输入法安装")
    parser.add_argument("-m", "--mosquitto", help="MQTT Broker安装")

    args = parser.parse_args()
    args = vars(args)
    print(args)
    if len(sys.argv) == 1:
        parser.print_help()
    service = Service()
    if args["wifi"]:
        service.connect_wifi()
    if args["version"]:
        service.get_version()
    if args["source"]:
        service.change_source()
    if args["prepare"]:
        service.prepare()
    if args["installHA"]:
        service.install_ha()
    if args["autostart"]:
        service.ha_auto_start()
    if args["samba"]:
        service.samba()
    if args["chinese"]:
        service.install_font_pinyin()
    if args["mosquitto"]:
        service.mosquitto()


if __name__ == '__main__':
    Install()
