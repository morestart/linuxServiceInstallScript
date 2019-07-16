import getopt
import subprocess
import sys
import time
import os
from pathlib import Path


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
        self.docker_mirror_path = "/etc/docker/daemon.json"
        self.flag = 0

    # 配置wifi
    def set_wifi(self):
        Logger.info("[INFO] 增加wifi配置,请输入你的用户名和密码...")
        SSID = input("SSID>")
        PASSWORD = input("PASSWORD>")

        if SSID != "":
            Logger.info("[INFO] 确认你的wifi配置.(y or n)")
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
                    Logger.info("[INFO] 配置成功!")
            elif confirm == "n" or confirm == "N":
                self.set_wifi()
        else:
            Logger.warn("[WARNING] SSID不能为空")
            self.set_wifi()

    # 获取当前Python版本
    @staticmethod
    def get_python_version():

        Logger.info("[INFO] Python3 版本")
        code = subprocess.run("python3 -V", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 未找到Python3")

        Logger.info("[INFO] Python2 版本")
        code = subprocess.run("python -V", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 未找到Python2")

    # 获取当前HA版本
    @staticmethod
    def get_ha_version():
        code = subprocess.run("hass --version", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 未安装HomeAssistant")

    # 换源 更换清华源 pip同步时间 5min
    def change_pip_source(self):
        code = subprocess.run("sudo mv /etc/pip.conf /etc/pip.conf.bak", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 没有找到pip文件,准备建立pip文件")

            time.sleep(2)
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                Logger.info("[INFO] 写入pip文件成功")

        elif code.returncode == 0:
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                Logger.info("[INFO] 写入pip文件成功")

    def change_apt_source(self):
        code = subprocess.run("sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak", shell=True)
        if code.returncode != 0:
            Logger.error("[INFO] 找不到apt文件,准备建立apt文件")
            time.sleep(2)
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
                Logger.info("[INFO] 写入apt文件成功")

        elif code.returncode == 0:
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
                Logger.info("[INFO] 写入apt文件成功")

        self.prepare()

    # 更新源与软件
    def prepare(self):
        Logger.info("[INFO] 准备更新软件包列表")

        code = subprocess.run("sudo apt-get update", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 更新软件包列表失败,请检查网络连接,两秒后准备重新更新")
            time.sleep(2)
            self.prepare()
        elif code.returncode == 0:
            Logger.info("[INFO] 软件包列表更新完毕")
            Logger.info("\n")
            Logger.info("[INFO] 是否更新软件?(y or n) 默认为n")

            confirm = input("(不输入可直接回车使用默认值)>")
            if confirm == "y" or confirm == "Y":
                code = subprocess.run("sudo apt-get upgrade", shell=True)
                if code.returncode != 0:
                    Logger.error("[ERROR] 更新软件失败,请检查网络连接")
                else:
                    Logger.info("[INFO] 更新软件完毕")
            else:
                pass

    # 更新HomeAssistant
    def upgrade_ha(self):
        Logger.info("[INFO] 准备更新HomeAssistant")

        code = subprocess.run("sudo pip3 install -U homeassistant", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 更新HomeAssistant失败,请检查网络, 两秒后准备重新安装...")
            time.sleep(2)
            self.upgrade_ha()

    # 更新指定版本HA
    def upgrade_specific_ha(self):
        Logger.info("[INFO] 请输入HA版本号")

        ha_version = input(">")
        code = subprocess.run("sudo pip3 install -U homeassistant=={}".format(ha_version), shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装{}版本HomeAssistant失败,请检查版本号与网络连接,"
                         "两秒后准备重新安装...".format(ha_version))
            time.sleep(2)
            self.upgrade_specific_ha()
        elif code.returncode == 0:
            Logger.info("[INFO] 安装{}版本HomeAssistant成功".format(ha_version))

    # 安装HomeAssistant
    def install_ha(self):
        Logger.info("[INFO] 开始安装HomeAssistant")

        code = subprocess.run("sudo pip3 install homeassistant", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装HomeAssistant失败,请检查网络连接,两秒后准备重新安装")
            time.sleep(2)
            self.install_ha()
        elif code.returncode == 0:
            self.start_ha()
            self.ha_auto_start()
            # 安装完成后提示用户是否打印HA运行日志
            confirm = input("是否查看HomeAssistant日志?(y or n)..")
            if confirm == "y" or confirm == "Y":
                self.print_ha_log()
            else:
                pass

    # HA 自启动
    def ha_auto_start(self):
        Logger.info("[INFO] 准备配置HomeAssistant自启动")

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
            Logger.info("[INFO] HomeAssistant自启动建立成功")
        except FileNotFoundError:
            Logger.error("[ERROR] 自启动建立失败,请检查自启动配置路径.")

    # samba安装 TODO
    def install_samba(self):
        Logger.info("[INFO] 准备安装Samba")

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
        Logger.info("[INFO] 安装Samba成功")

    # 安装 mosquitto
    def install_mosquitto(self):
        Logger.info("[INFO] 准备安装Mosquitto")

        self.prepare()
        code = subprocess.run("sudo apt-get install mosquitto", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装mosquitto失败,请检查网络连接,两秒后准备重新安装")

            time.sleep(2)
            self.install_mosquitto()
        elif code.returncode == 0:
            try:
                with open(self.mosquitto_config_path, "w+") as f:
                    f.write("allow_anonymous false\n"
                            "password_file /etc/mosquitto/pwfile\n"
                            "listener 1883\n")
                    Logger.info("[INFO] 写入MQTT配置成功!")

            except FileNotFoundError:
                Logger.error("[ERROR] 未发现mqtt配置文件,请重新安装...")

            mqtt_user_name = input("请输入MQTT用户名:")

            subprocess.run("sudo mosquitto_passwd -c /etc/mosquitto/pwfile {}".format(mqtt_user_name), shell=True)
            subprocess.run("sudo systemctl start mosquitto.service", shell=True)
            Logger.info("[INFO] MQTT安装配置成功")

    # 重启HA
    @staticmethod
    def restart_ha():
        code = subprocess.run("sudo systemctl restart home-assistant@pi", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 重启HomeAssistant失败")
        else:
            Logger.info("[INFO] 重启HomeAssistant成功")

    @staticmethod
    def start_ha():
        code = subprocess.run("sudo systemctl start home-assistant@pi", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 启动HomeAssistant失败")
        else:
            Logger.info("[INFO] 启动HomeAssistant成功")

    @staticmethod
    def stop_ha():
        code = subprocess.run("sudo systemctl stop home-assistant@pi", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 停止HomeAssistant失败")
        else:
            Logger.info("[INFO] 停止HomeAssistant成功")

    # 查看log
    @staticmethod
    def print_ha_log():
        code = subprocess.run("sudo journalctl -f -u home-assistant@pi", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 查看HomeAssistant日志失败")
        else:
            Logger.info("[INFO] 查看HomeAssistant日志成功")

    # 更新Python3版本
    def upgrade_python(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        pv = 'Python-3.7.2'
        Logger.info("[INFO] 准备安装{}".format(pv))

        Logger.info("[INFO] 准备卸载冲突, 如果有请选择y")

        code = subprocess.run("sudo pip3 uninstall homeassistant", shell=True)
        if code.returncode != 0:
            pass
        Logger.info("[INFO] 开始安装依赖")

        time.sleep(2)
        code = subprocess.run("sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev",
                              shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装依赖失败,请检查网络连接,两秒后准备重新安装")

            time.sleep(2)
            self.upgrade_python()
        elif code.returncode == 0:
            code = subprocess.run("sudo apt-get install wget", shell=True)
            if code.returncode != 0:
                Logger.error("[ERROR] 下载wget失败,请检查网络连接,两秒后准备重新安装")
                time.sleep(2)
                self.prepare()
            elif code.returncode == 0:
                file_dir = base_dir + '/'.format(pv) + '.tgz'
                file = Path(file_dir)
                if file.is_file():
                    Logger.info("[INFO] 开始解压安装包")
                    time.sleep(2)
                    subprocess.run("sudo tar -zvxf {}.tgz".format(pv), shell=True)
                    os.chdir("{}/{}".format(base_dir, pv))
                    Logger.info("[INFO] 开始编译{}".format(pv))
                    time.sleep(2)
                    subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
                    Logger.info("[INFO] 已完成{}安装".format(pv))
                else:
                    Logger.info("[INFO] 下载Python安装包")
                    time.sleep(2)
                    code = subprocess.run("sudo wget https://www.python.org/ftp/python/3.7.2/{}.tgz".format(pv),
                                          shell=True)
                    if code.returncode != 0:
                        Logger.error("[ERROR] 下载Python失败,请检查网络连接,两秒后准备重新安装")
                        time.sleep(2)
                        self.upgrade_python()
                    elif code.returncode == 0:
                        Logger.info("[INFO] 开始解压安装包")
                        time.sleep(2)
                        subprocess.run("sudo tar -zvxf {}.tgz".format(pv), shell=True)
                        os.chdir("{}/{}".format(base_dir, pv))
                        Logger.info("[INFO] 开始编译{}".format(pv))
                        time.sleep(2)
                        subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
                        Logger.info("[INFO] 已完成{}安装".format(pv))

        Logger.info("\n")
        # os.remove(pv + '.tgz')
        self.get_python_version()

    #  安装docker ce
    def install_docker(self):

        Logger.info("[INFO] 准备安装docker CE")
        if self.flag == 0:
            self.prepare()
            self.flag = 1
        Logger.info("[INFO] 准备安装docker CE依赖")
        code = subprocess.run("sudo apt-get install apt-transport-https ca-certificates gnupg2 lsb-release software-properties-common", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装依赖失败,2s后准备重新安装...")
            time.sleep(2)
            self.install_docker()
        else:
            Logger.info("[INFO] 准备添加GPG秘钥")
            code = subprocess.run("curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/raspbian/gpg | sudo apt-key "
                                  "add -", shell=True)
            if code.returncode != 0:
                Logger.error("[ERROR] 添加秘钥失败,2s后准备重新添加")
                time.sleep(2)
                self.install_docker()
            else:
                Logger.info("[INFO] 准备添加国内镜像源")
                with open(self.apt_source_path, 'a') as f:
                    f.write("deb https://download.docker.com/linux/raspbian stretch stable")
                self.prepare()
                # TODO: 安装docker ce
                code = subprocess.run("sudo apt-get install docker-ce", shell=True)
                if code.returncode != 0:
                    Logger.error("[ERROR] docker CE安装失败,准备重新安装...")
                    self.install_docker()
                else:
                    Logger.info("[INFO] 准备建立用户组")
                    # 建立docker 用户组
                    subprocess.run("sudo groupadd docker", shell=True)
                    # 当前用户加入用户组
                    subprocess.run("sudo usermod -aG docker $USER", shell=True)
                    # 测试docker是否安装成功
                    Logger.info("[INFO] 验证docker是否安装成功")
                    subprocess.run("docker run arm32v7/hello-world", shell=True)
                    Logger.info("[INFO] 准备启动docker CE")
                    subprocess.run("sudo systemctl enable docker", shell=True)
                    subprocess.run("sudo systemctl start docker", shell=True)
                    # Logger.info("[INFO] 配置镜像加速器")
                    # with open(self.docker_mirror_path, "w+") as f:
                    #     f.write()


class UbuntuService:
    def __init__(self):
        pass

    def upgrade_python(self):
        subprocess.run("sudo apt-get install wget", shell=True)
        subprocess.run("wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz", shell=True)
        subprocess.run("tar -xvzf Python-3.7.4.tgz", shell=True)
        os.chdir("Python-3.7.4")
        subprocess.run("./configure --with-ssl --prefix=/usr/local/python3", shell=True)
        subprocess.run("sudo apt-get update && sudo apt-get install build-essential python-dev python-setuptools python-pip", shell=True)
        subprocess.run("sudo make && sudo make install", shell=True)
        subprocess.run("sudo rm -rf /usr/bin/python3", shell=True)
        subprocess.run("sudo rm -rf /usr/bin/pip3", shell=True)
        subprocess.run("sudo ln -s /usr/local/python3/bin/python3.7 /usr/bin/python3", shell=True)
        subprocess.run("sudo ln -s /usr/local/python3/bin/pip3.7 /usr/bin/pip3", shell=True)



class Install:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-w-p-s-h", ["help", "pv", "hv", "cps", "cas", "uh", "ih", "has", "im",
                                                              "rh", "phl", "up", "ush", "sh", "sth", "id", "uup"])
        service = Service()
        ubuntuservice = UbuntuService()
        for opt, value in opts:
            if opt == "-h" or opt == "--help":
                Logger.info("-h 显示帮助")
                Logger.info("-w 添加wifi配置")
                Logger.info("-p 更新软件包列表与软件")
                Logger.info("-s 安装samba服务")
                Logger.info("--im 安装mosquitto")
                Logger.info("-" * 30)
                Logger.info("--cps 更换pip源")
                Logger.info("--cas 更换apt源")
                Logger.info("-" * 30)
                Logger.info("--ih 安装HomeAssistant")
                Logger.info("--uh 更新HomeAssistant")
                Logger.info("--has 配置HomeAssistant自启动")
                Logger.info("--sh 运行HomeAssistant实例")
                Logger.info("--sth 停止HomeAssistant实例")
                Logger.info("--rh 重启HomeAssistant")
                Logger.info("--phl 查看HomeAssistant日志")
                Logger.info("--hv 查看HomeAssistant版本")
                Logger.info("-" * 30)
                Logger.info("--pv 查看Python版本")
                Logger.info("--up 更新Python3版本")
                Logger.info("-" * 30)
                Logger.info("--id 安装docker CE")

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
            elif opt == "--id":
                service.install_docker()
            elif opt == "-uup":
                ubuntuservice.upgrade_python()
    except getopt.GetoptError:
        Logger.error("[ERROR] 没有这个选项, 请使用-h或--help查看可用选项")


if __name__ == '__main__':
    try:
        Install()
    except PermissionError:
        Logger.error("[ERROR] 权限不足,请使用sudo权限运行此程序")
