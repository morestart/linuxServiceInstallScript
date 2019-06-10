import subprocess
import time
import sys, getopt


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
        self.pip_source_path = "/etc/pip.conf"
        self.apt_source_path = "/etc/apt/sources.list"
        self.auto_start_conf_add = "/etc/systemd/system/home-assistant@pi.service"
        self.smb_conf_path = "/etc/samba/smb.conf"
        self.wifi_conf_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
        self.mosquitto_config_path = "/etc/mosquitto/mosquitto.conf"

    # 配置wifi
    def set_wifi(self):
        Logger.info(">>>增加wifi配置,请输入你的用户名和密码...")
        SSID = input("SSID>")
        PASSWORD = input("PASSWORD>")

        if SSID != "":
            Logger.info(">>>确认你的wifi配置.(y or n)")
            confirm = input(">")
            if confirm == "y" or confirm == "Y":
                with open(self.wifi_conf_path, "w+") as f:
                    f.write("country=CN\n"
                            "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n"
                            "update_config=1\n"
                            "network={\n"
                            "\tssid=\"" + SSID + "\"\n" +
                            "\tpsk=\"" + PASSWORD + "\"\n" +
                            "\tkey_mgmt=WPA-PSK\n"
                            "\tpriority=1}")
                    Logger.info("配置成功!")
            elif confirm == "n" or confirm == "N":
                self.set_wifi()
        else:
            Logger.warn("⚠️,SSID不能为空")
            self.set_wifi()

    # 获取当前Python版本
    @staticmethod
    def get_python_version():
        subprocess.run("python3 -V", shell=True)

    # 获取当前HA版本
    @staticmethod
    def get_ha_version():
        subprocess.run("hass --version", shell=True)

    # 换源 更换清华源 pip同步时间 5min
    def change_pip_source(self):
        try:
            subprocess.run("sudo mv /etc/pip.conf /etc/pip.conf.bak", shell=True)
        except FileNotFoundError:
            Logger.error(">>>没有找到pip文件,准备建立pip文件")
            time.sleep(2)
        finally:
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                Logger.info(">>>写入pip文件成功")
                time.sleep(1)

    def change_apt_source(self):
        try:
            subprocess.run("sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak", shell=True)
        except FileNotFoundError:
            Logger.error(">>>找不到apt文件,准备建立apt文件")
            time.sleep(2)
        finally:
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
                Logger.info(">>>写入apt文件成功")
                time.sleep(1)
        self.prepare()

    # 更新源与软件
    @staticmethod
    def prepare():
        subprocess.run("sudo apt-get update", shell=True)
        Logger.info(">>>软件包列表更新完毕")
        Logger.info("\n")
        Logger.info(">>>是否更新软件?(y or n)")
        confirm = input(">")
        if confirm == "y" or confirm == "Y":
            subprocess.run("sudo apt-get upgrade", shell=True)
            Logger.info(">>>更新apt源完毕")
        elif confirm == "n" or confirm == "N":
            pass

    # 更新HomeAssistant
    @staticmethod
    def upgrade_ha():
        subprocess.run("sudo pip3 install -U homeassistant", shell=True)

    # 更新指定版本HA
    def upgrade_specific_ha(self):
        try:
            Logger.info(">>>请输入HA版本号")
            ha_version = input(">")
            subprocess.run("sudo pip3 install -U homeassistant={}".format(ha_version), shell=True)
        except Exception as e:
            Logger.error(e)
            Logger.error(">>>没有这个版本的HA, 请重新输入.")
            self.upgrade_specific_ha()

    # 安装HomeAssistant
    def install_ha(self):
        try:
            subprocess.run("sudo pip3 install homeassistant", shell=True)
        except Exception as e:
            Logger.error(e)
            Logger.error(">>>安装失败, 准备重新安装")
            self.install_ha()
        self.ha_auto_start()

    # HA 自启动
    def ha_auto_start(self):
        try:
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
            Logger.info(">>>HomeAssistant自启动建立成功")
        except Exception as e:
            Logger.error(e)
            Logger.error(">>>自启动建立失败,请检查自启动配置路径.")

    # samba安装
    def install_samba(self):
        subprocess.run("sudo apt-get install samba samba-common", shell=True)
        subprocess.run("sudo smbpasswd -a pi", shell=True)
        subprocess.run("sudo rm " + self.smb_conf_path, shell=True)
        with open(self.smb_conf_path, "w") as f:
            f.write("[global]\n"
                    "netbios name = raspberrypi\n"
                    "server string = The Pi File Center\n"
                    "workgroup = WORKGROUP\n"
                    "hosts allow =\n"
                    "remote announce =\n"
                    "remote browse sync =\n"
                    "[HOME ASSISTANT]\n"
                    "path = /home/pi\n"
                    "comment = No comment\n"
                    "browsable = yes\n"
                    "read only = no\n"
                    "valid users =\n"
                    "writable = yes\n"
                    "guest ok = yes\n"
                    "public = yes\n"
                    "create mask = 0777\n"
                    "directory mask = 0777\n"
                    "force user = root\n"
                    "force create mode = 0777\n"
                    "force directory mode = 0777\n"
                    "hosts allow =\n")
        subprocess.run("sudo systemctl restart smbd", shell=True)

    # 字体和输入法安装
    @staticmethod
    def install_font_pinyin():
        subprocess.run("sudo apt-get install fonts-wqy-zenhei -y", shell=True)
        subprocess.run("sudo apt-get install scim-pinyin -y", shell=True)
        Logger.info(">>>字体输入法安装成功")

    # 安装 mosquitto
    def install_mosquitto(self):
        subprocess.run("sudo apt-get install mosquitto", shell=True)
        try:
            with open(self.mosquitto_config_path, "w+") as f:
                f.write("allow_anonymous false\n"
                        "password_file /etc/mosquitto/pwfile\n"
                        "listener 1883\n")
                Logger.info(">>>写入MQTT配置成功!")
        except Exception as e:
            Logger.error(e)
            Logger.error(">>>找不到MQTT配置,请检查路径.")
        mqtt_user_name = input("请输入MQTT用户名>")
        subprocess.run("sudo mosquitto_passwd -c /etc/mosquitto/pwfile {}".format(mqtt_user_name), shell=True)
        subprocess.run("sudo systemctl start mosquitto.service", shell=True)

    # 重启HA
    @staticmethod
    def restart_ha():
        subprocess.run("sudo systemctl restart home-assistant@pi", shell=True)

    # 查看log
    @staticmethod
    def print_ha_log():
        subprocess.run("sudo journalctl -f -u home-assistant@pi", shell=True)

    @staticmethod
    def upgrade_python():
        import os
        Logger.info(">>>开始安装依赖")
        time.sleep(2)
        subprocess.run("sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev", shell=True)
        subprocess.run("sudo apt-get install wget", shell=True)
        Logger.info(">>>下载Python安装包")
        time.sleep(2)
        subprocess.run("wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz", shell=True)
        Logger.info(">>>开始解压安装包")
        time.sleep(1)
        subprocess.run("sudo tar -zvxf Python-3.7.2.tgz", shell=True)
        os.chdir("/home/pi/Python-3.7.2")
        Logger.info(">>>开始编译Python")
        time.sleep(2)
        subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
        Logger.info(">>>建立链接")
        time.sleep(1)
        subprocess.run("sudo mv /usr/bin/python /usr/bin/python3.4.2", shell=True)
        subprocess.run("ln -s /usr/local/python37/bin/python37 /usr/bin/python", shell=True)


class Install:
    opts, args = getopt.getopt(sys.argv[1:], "-w-p-s", ["help", "pv", "hv", "cps", "cas", "uh",
                                                        "ih", "has", "ifp", "im", "rh", "phl", "up", "ush"])
    service = Service()
    for opt, value in opts:
        if opt == "-w":
            service.set_wifi()
        elif opt == "-p":
            service.prepare()
        elif opt == "-s":
            service.install_samba()
        elif opt == "--pv":
            service.get_python_version()
        elif opt == "--hv":
            service.get_ha_version()
        elif opt == "--cps":
            service.change_pip_source()
        elif opt == "--cas":
            service.change_apt_source()
        elif opt == "--uh":
            service.upgrade_ha()
        elif opt == "--usp":
            service.upgrade_specific_ha()
        elif opt == "--ih":
            service.install_ha()
        elif opt == "--has":
            service.ha_auto_start()
        elif opt == "--ifp":
            service.install_font_pinyin()
        elif opt == "--im":
            service.install_mosquitto()
        elif opt == "--rh":
            service.restart_ha()
        elif opt == "--phl":
            service.print_ha_log()
        elif opt == "--up":
            service.upgrade_python()


if __name__ == '__main__':
    Install()
