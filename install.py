import getopt
import subprocess
import sys
import time
import locale
import os
from pathlib import Path

language = locale.getdefaultlocale()[0]


class Logger:
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'

    @staticmethod
    def info(info):
        try:
            print(Logger.OKBLUE + info + Logger.ENDC)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not, we will use english..")

    @staticmethod
    def warn(info):
        try:
            print(Logger.WARNING + info + Logger.ENDC)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not, we will use english..")

    @staticmethod
    def error(info):
        try:
            print(Logger.FAIL + info + Logger.ENDC)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not, we will use english..")


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
        if language == 'zh_CN':
            Logger.info("[INFO] 增加wifi配置,请输入你的用户名和密码...")
        else:
            Logger.info("[INFO] add wifi config, please input your user name and password...")
        SSID = input("SSID>")
        PASSWORD = input("PASSWORD>")

        if SSID != "":
            if language == 'zh_CN':
                Logger.info("[INFO] 确认你的wifi配置.(y or n)")
            else:
                Logger.info("[INFO] please confirm your wifi config")
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
                    if language == 'zh_CN':
                        Logger.info("[INFO] 配置成功!")
                    else:
                        Logger.info("[INFO] config success!")
            elif confirm == "n" or confirm == "N":
                self.set_wifi()
        else:
            if language == 'zh_CN':
                Logger.warn("[WARNING] SSID不能为空")
            else:
                Logger.warn("[WARNING] SSID is None! Please input again")
            self.set_wifi()

    # 获取当前Python版本
    @staticmethod
    def get_python_version():
        if language == 'zh_CN':
            Logger.info("[INFO] Python3 版本")
        else:
            Logger.info("[INFO] Python3 version")
        code = subprocess.run("python3 -V", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 未找到Python3")
            else:
                Logger.error("[ERROR] can't find python3")
        if language == 'zh_CN':
            Logger.info("[INFO] Python2 版本")
        else:
            Logger.info("[INFO] Python3 version")
        code = subprocess.run("python -V", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 未找到Python2")
            else:
                Logger.error("[ERROR] can't find python2")

    # 获取当前HA版本
    @staticmethod
    def get_ha_version():
        code = subprocess.run("hass --version", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 未安装HomeAssistant")
            else:
                Logger.error("[ERROR] No HomeAssistant installed")

    # 换源 更换清华源 pip同步时间 5min
    def change_pip_source(self):
        code = subprocess.run("sudo mv /etc/pip.conf /etc/pip.conf.bak", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 没有找到pip文件,准备建立pip文件")
            else:
                Logger.error("[ERROR] can't find pip file, we will create this file")
            time.sleep(2)
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                if language == 'zh_CN':
                    Logger.info("[INFO] 写入pip文件成功")
                else:
                    Logger.info("[INFO] write pip file success")
        elif code.returncode == 0:
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                if language == 'zh_CN':
                    Logger.info("[INFO] 写入pip文件成功")
                else:
                    Logger.info("[INFO] write pip file success")

    def change_apt_source(self):
        code = subprocess.run("sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[INFO] 找不到apt文件,准备建立apt文件")
            else:
                Logger.info("[INFO] can't find apt file, we will create apt file")
            time.sleep(2)
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
                if language == 'zh_CN':
                    Logger.info("[INFO] 写入apt文件成功")
                else:
                    Logger.info("[INFO] write apt file success")
        elif code.returncode == 0:
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
                if language == 'zh_CN':
                    Logger.info("[INFO] 写入apt文件成功")
                else:
                    Logger.info("[INFO] write apt file success")
        self.prepare()

    # 更新源与软件
    def prepare(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 准备更新软件包列表")
        else:
            Logger.info("[INFO] Prepare update software list")
        code = subprocess.run("sudo apt-get update", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 更新软件包列表失败,请检查网络连接,两秒后准备重新更新")
            else:
                Logger.info("[ERROR] update software list fail, please check the internet, we will prepare "
                            "to start this job after 2 seconds")
            time.sleep(2)
            self.prepare()
        elif code.returncode == 0:
            if language == 'zh_CN':
                Logger.info("[INFO] 软件包列表更新完毕")
                Logger.info("\n")
                Logger.info("[INFO] 是否更新软件?(y or n)")
            else:
                Logger.info("[INFO] software list is already update")
                Logger.info("\n")
                Logger.info("[INFO] will you want to upgrade the software?(y or n)")
            confirm = input(">")
            if confirm == "y" or confirm == "Y":
                code = subprocess.run("sudo apt-get upgrade", shell=True)
                if code.returncode != 0:
                    if language == 'zh_CN':
                        Logger.error("[ERROR] 更新软件失败,请检查网络连接")
                    else:
                        Logger.error("[ERROR] Update software failed, please check network connection")
                else:
                    if language == 'zh_CN':
                        Logger.info("[INFO] 更新软件完毕")
                    else:
                        Logger.info("[INFO] Update software completed")
            elif confirm == "n" or confirm == "N":
                pass
            else:
                pass

    # 更新HomeAssistant
    def upgrade_ha(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 准备更新HomeAssistant")
        else:
            Logger.info("[INFO] Prepare upgrade HomeAssistant")
        code = subprocess.run("sudo pip3 install -U homeassistant", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 更新HomeAssistant失败,请检查网络, 两秒后准备重新安装...")
            else:
                Logger.error("[ERROR] Updating HomeAssistant failed. Please check the network and prepare "
                             "for reinstallation in two seconds....")
            time.sleep(2)
            self.upgrade_ha()

    # 更新指定版本HA
    def upgrade_specific_ha(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 请输入HA版本号")
        else:
            Logger.info("[INFO] Please enter HA version number")
        ha_version = input(">")
        code = subprocess.run("sudo pip3 install -U homeassistant=={}".format(ha_version), shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 安装{}版本HomeAssistant失败,请检查版本号与网络连接,"
                             "两秒后准备重新安装...".format(ha_version))
            else:
                Logger.error("[ERROR] Installation of {} version HomeAssistant failed. "
                             "Please check the version number for "
                             "network connection and prepare for reinstallation in two seconds....".format(ha_version))
            time.sleep(2)
            self.upgrade_specific_ha()
        elif code.returncode == 0:
            if language == 'zh_CN':
                Logger.info("[INFO] 安装{}版本HomeAssistant成功".format(ha_version))
            else:
                Logger.info("[INFO] Installation of {} version HomeAssistant succeed.".format(ha_version))

    # 安装HomeAssistant
    def install_ha(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 开始安装HomeAssistant")
        else:
            Logger.info("[INFO] Start installation HomeAssistant")

        code = subprocess.run("sudo pip3 install homeassistant", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 安装HomeAssistant失败,请检查网络连接,两秒后准备重新安装")
            else:
                Logger.error("[ERROR] Installation HomeAssistant failed. "
                             "Please check the version number for "
                             "network connection and prepare for reinstallation in two seconds....")
            time.sleep(2)
            self.install_ha()
        elif code.returncode == 0:
            self.start_ha()
            self.ha_auto_start()
            # 安装完成后提示用户是否打印HA运行日志
            if language == 'zh_CN':
                confirm = input("是否查看HomeAssistant日志?(y or n)..")
                if confirm == "y" or confirm == "Y":
                    self.print_ha_log()
                elif confirm == "n" or confirm == "n":
                    pass
            else:
                confirm = input("Do you want to see HomeAssistant log?(y or n)..")
                if confirm == "y" or confirm == "Y":
                    self.print_ha_log()
                elif confirm == "n" or confirm == "n":
                    pass

    # HA 自启动
    def ha_auto_start(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 准备配置HomeAssistant自启动")
        else:
            Logger.info("[INFO] Prepare to configure HomeAssistant self-startup")
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
                        "WantedBy=multi-user.target\n")
            if language == 'zh_CN':
                Logger.info("[INFO] HomeAssistant自启动建立成功")
            else:
                Logger.info("[INFO] HomeAssistant Self-Start Establishment Successful")
        except FileNotFoundError:
            if language == 'zh_CN':
                Logger.error("[ERROR] 自启动建立失败,请检查自启动配置路径.")
            else:
                Logger.error("[ERROR] Self-startup setup failed. Check the self-startup configuration path.")

    # samba安装 TODO
    def install_samba(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 准备安装Samba")
        else:
            Logger.info("[INFO] Prepare to install Samba")
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

    # 安装 mosquitto
    def install_mosquitto(self):
        if language == 'zh_CN':
            Logger.info("[INFO] 准备安装Mosquitto`")
        else:
            Logger.info("[INFO] Prepare to install Mosquitto")
        self.prepare()
        code = subprocess.run("sudo apt-get install mosquitto", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 安装mosquitto失败,请检查网络连接,两秒后准备重新安装")
            else:
                Logger.error("[ERROR] Installation of mosquitto failed. Please check the network "
                             "connection and prepare for reinstallation in two seconds")
            time.sleep(2)
            self.install_mosquitto()
        elif code.returncode == 0:
            try:
                with open(self.mosquitto_config_path, "w+") as f:
                    f.write("allow_anonymous false\n"
                            "password_file /etc/mosquitto/pwfile\n"
                            "listener 1883\n")
                    if language == 'zh_CN':
                        Logger.info("[INFO] 写入MQTT配置成功!")
                    else:
                        Logger.info("[INFO] Write MQTT Configuration Successful!")
            except FileNotFoundError:
                if language == 'zh_CN':
                    Logger.error("[ERROR] MQTT configuration could not be found. Check the path.")
                else:
                    Logger.error("[ERROR] ")
            if language == 'zh_CN':
                mqtt_user_name = input("请输入MQTT用户名:")
            else:
                mqtt_user_name = input("Please input mqtt user name:")
            subprocess.run("sudo mosquitto_passwd -c /etc/mosquitto/pwfile {}".format(mqtt_user_name), shell=True)
            subprocess.run("sudo systemctl start mosquitto.service", shell=True)

    # 重启HA
    @staticmethod
    def restart_ha():
        code = subprocess.run("sudo systemctl restart home-assistant@pi", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 重启HomeAssistant失败")
            else:
                Logger.error("[ERROR] restart HomeAssistant filed")
        else:
            if language == 'zh_CN':
                Logger.info("[INFO] 重启HomeAssistant成功")
            else:
                Logger.info('[INFO] restart HomeAssistant success')

    @staticmethod
    def start_ha():
        code = subprocess.run("sudo systemctl start home-assistant@pi", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 启动HomeAssistant失败")
            else:
                Logger.error("[ERROR] start HomeAssistant filed")
        else:
            if language == 'zh_CN':
                Logger.info("[INFO] 启动HomeAssistant成功")
            else:
                Logger.info('[INFO] start HomeAssistant success')

    @staticmethod
    def stop_ha():
        code = subprocess.run("sudo systemctl stop home-assistant@pi", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 停止HomeAssistant失败")
            else:
                Logger.error("[ERROR] stop HomeAssistant filed")
        else:
            if language == 'zh_CN':
                Logger.info("[INFO] 停止HomeAssistant成功")
            else:
                Logger.info('[INFO] stop HomeAssistant success')

    # 查看log
    @staticmethod
    def print_ha_log():
        code = subprocess.run("sudo journalctl -f -u home-assistant@pi", shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 查看HomeAssistant日志失败")
            else:
                Logger.error("[ERROR] view HomeAssistant log file filed")
        else:
            if language == 'zh_CN':
                Logger.info("[INFO] 查看HomeAssistant日志成功")
            else:
                Logger.info('[INFO] view HomeAssistant log file success')

    def upgrade_python(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        pv = 'Python-3.7.3'
        if language == 'zh_CN':
            Logger.info("[INFO] 准备安装{}".format(pv))
        else:
            Logger.info("[INFO] Prepare to install Samba")

        if language == 'zh_CN':
            Logger.info("[INFO] 准备更新Python3版本")
            Logger.info("[INFO] 准备卸载冲突, 如果有请选择y")
        else:
            Logger.info("[INFO] Ready to update Python 3")
            Logger.info("[INFO] Preparing for Unloading Conflict")

        code = subprocess.run("sudo pip3 uninstall homeassistant", shell=True)
        if code.returncode != 0:
            pass
        if language == 'zh_CN':
            Logger.info("[INFO] 开始安装依赖")
        else:
            Logger.info("[INFO] Start installing dependencies")
        time.sleep(2)
        code = subprocess.run("sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev",
                              shell=True)
        if code.returncode != 0:
            if language == 'zh_CN':
                Logger.error("[ERROR] 安装依赖失败,请检查网络连接,两秒后准备重新安装")
            else:
                Logger.error("[ERROR] Installation dependency failed. Please check the network connection "
                             "and prepare for reinstallation in two seconds.")

            time.sleep(2)
            self.upgrade_python()
        elif code.returncode == 0:
            code = subprocess.run("sudo apt-get install wget", shell=True)
            if code.returncode != 0:
                if language == 'zh_CN':
                    Logger.error("[ERROR] 下载wget失败,请检查网络连接,两秒后准备重新安装")
                else:
                    Logger.error("[ERROR] The download of wget failed. Please check the network connection and "
                                 "prepare for reinstallation in two seconds.")
                time.sleep(2)
                self.prepare()
            elif code.returncode == 0:
                file_dir = base_dir + '/'.format(pv) + '.tgz'
                file = Path(file_dir)
                if file.is_file():
                    if language == 'zh_CN':
                        Logger.info("[INFO] 开始解压安装包")
                    else:
                        Logger.info("[INFO] Start decompressing the installation package")
                    time.sleep(2)
                    subprocess.run("sudo tar -zvxf {}.tgz".format(pv), shell=True)
                    os.chdir("{}/{}".format(base_dir, pv))
                    if language == 'zh_CN':
                        Logger.info("[INFO] 开始编译{}".format(pv))
                    else:
                        Logger.info("[INFO] Start compiling Python")
                    time.sleep(2)
                    subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
                    if language == 'zh_CN':
                        Logger.info("[INFO] 已完成{}安装".format(pv))
                    else:
                        Logger.info("[INFO] {} installation completed".format(pv))
                else:
                    if language == 'zh_CN':
                        Logger.info("[INFO] 下载Python安装包")
                    else:
                        Logger.info("[INFO] Download the Python installation package")
                    time.sleep(2)
                    code = subprocess.run("sudo wget https://www.python.org/ftp/python/3.7.3/{}.tgz".format(pv),
                                          shell=True)
                    if code.returncode != 0:
                        if language == 'zh_CN':
                            Logger.error("[ERROR] 下载Python失败,请检查网络连接,两秒后准备重新安装")
                        else:
                            Logger.error("[ERROR] Download Python failed. Please check your network connection and "
                                         "prepare to reinstall it in two seconds.")
                        time.sleep(2)
                        self.upgrade_python()
                    elif code.returncode == 0:
                        if language == 'zh_CN':
                            Logger.info("[INFO] 开始解压安装包")
                        else:
                            Logger.info("[INFO] Start decompressing the installation package")
                        time.sleep(2)
                        subprocess.run("sudo tar -zvxf {}.tgz".format(pv), shell=True)
                        os.chdir("{}/{}".format(base_dir, pv))
                        if language == 'zh_CN':
                            Logger.info("[INFO] 开始编译{}".format(pv))
                        else:
                            Logger.info("[INFO] Start compiling Python")
                        time.sleep(2)
                        subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
                        if language == 'zh_CN':
                            Logger.info("[INFO] 已完成{}安装".format(pv))
                        else:
                            Logger.info("[INFO] {} installation completed".format(pv))
        Logger.info("\n")
        os.remove(pv + '.tgz')
        self.get_python_version()


class Install:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-w-p-s-h", ["help", "pv", "hv", "cps", "cas", "uh", "ih", "has", "im",
                                                              "rh", "phl", "up", "ush", "sh", "sth"])
        service = Service()
        for opt, value in opts:
            if opt == "-h" or opt == "--help":
                if language == 'zh_CN':
                    Logger.info("-h 显示帮助")
                    Logger.info("-w 添加wifi配置")
                    Logger.info("-p 更新软件包列表与软件")
                    Logger.info("-s 安装samba服务")
                    Logger.info("--im 安装mosquitto")
                    Logger.info("-" * 20)
                    Logger.info("--cps 更换pip源")
                    Logger.info("--cas 更换apt源")
                    Logger.info("-" * 20)
                    Logger.info("--ih 安装HomeAssistant")
                    Logger.info("--uh 更新HomeAssistant")
                    Logger.info("--has 配置HomeAssistant自启动")
                    Logger.info("--sh 运行HomeAssistant实例")
                    Logger.info("--sth 停止HomeAssistant实例")
                    Logger.info("--rh 重启HomeAssistant")
                    Logger.info("--phl 查看HomeAssistant日志")
                    Logger.info("--hv 查看HomeAssistant版本")
                    Logger.info("-" * 20)
                    Logger.info("--pv 查看Python版本")
                    Logger.info("--up 更新Python3版本")
                else:
                    Logger.info("-h get help info")
                    Logger.info("-w add wifi config")
                    Logger.info("-p Updating Package List and Software")
                    Logger.info("-s Installing Samba services")
                    Logger.info("--im Installing mosquitto services")
                    Logger.info("-" * 20)
                    Logger.info("--cps change pip source")
                    Logger.info("--cas change apt source")
                    Logger.info("-" * 20)
                    Logger.info("--ih install HomeAssistant")
                    Logger.info("--uh upgrade HomeAssistant")
                    Logger.info("--has set HomeAssistant auto start")
                    Logger.info("--sh run HomeAssistant")
                    Logger.info("--sth stop HomeAssistant")
                    Logger.info("--rh restart HomeAssistant")
                    Logger.info("--phl get HomeAssistant log")
                    Logger.info("--hv get HomeAssistant version")
                    Logger.info("-" * 20)
                    Logger.info("--pv get Python version")
                    Logger.info("--up upgrade Python3 version")
            elif opt == "-w":
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
            elif opt == "--im":
                service.install_mosquitto()
            elif opt == "--rh":
                service.restart_ha()
            elif opt == "--phl":
                service.print_ha_log()
            elif opt == "--up":
                service.upgrade_python()
            elif opt == "--sh":
                service.start_ha()
            elif opt == "--sth":
                service.stop_ha()
    except getopt.GetoptError:
        if language == 'zh_CN':
            Logger.error("[ERROR] 没有这个选项, 请使用-h或--help查看可用选项")
        else:
            Logger.error("[ERROR] Without this option, use -h or --help to view available options")


if __name__ == '__main__':
    try:
        Install()
    except PermissionError:
        if language == 'zh_CN':
            Logger.error("[ERROR] 权限不足,请使用sudo权限运行此程序")
        else:
            Logger.error("[ERROR] Insufficient privileges, use sudo privileges to run this program")
