import getopt
import subprocess
import sys
import time
import os
from pathlib import Path
import getpass


class Logger:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[31m'
    END = '\033[0m'

    @staticmethod
    def info(info):
        try:
            print(Logger.OK + info + Logger.END)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not, we will use english..")

    @staticmethod
    def warn(info):
        try:
            print(Logger.WARNING + info + Logger.END)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not, we will use english..")

    @staticmethod
    def error(info):
        try:
            print(Logger.FAIL + info + Logger.END)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not, we will use english..")


# 公共服务 各系统兼容的部分
class BaseService:
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

    # 更新Python3版本
    def upgrade_python3(self):
        return

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

    # 获取当前HA版本
    @staticmethod
    def get_ha_version():
        code = subprocess.run("hass --version", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 未安装HomeAssistant")

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

    def set_wifi(self):
        return "不支持当前系统"


class UbuntuService(BaseService):
    def __init__(self):
        super().upgrade_python3()

    def upgrade_python3(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        Logger.info("[INFO] 准备更新Ubuntu Python3版本")
        self.prepare()
        Logger.info("[INFO] 准备安装依赖")
        code = subprocess.run(
            "sudo apt install wget && sudo apt install zlib* && sudo apt install libffi-dev "
            "&& sudo apt install openssl && sudo apt install libssl-dev && sudo apt install make",
            shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装依赖失败")
            self.upgrade_python3()
        else:
            Logger.info("[INFO] 安装依赖成功")

        Logger.info("[INFO] 准备下载Python3")
        code = subprocess.run("wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 下载Python3失败,准备重新下载...")
            self.upgrade_python3()
        else:
            Logger.info("[INFO] 下载Python3成功")

        Logger.info("[INFO] 准备安装GCC")
        code = subprocess.run("sudo apt install gcc", shell=True)
        if code.returncode != 0:
            Logger.error("[ERROR] 安装gcc失败,准备重新安装...")
            self.upgrade_python3()
        else:
            Logger.info("[INFO] 安装gcc成功")
        Logger.info("[INFO] 准备解压python")
        subprocess.run("tar -xvzf Python-3.7.4.tgz", shell=True)
        os.chdir("{}/Python-3.7.4".format(base_dir))
        # sudo apt install gcc
        subprocess.run("./configure", shell=True)
        subprocess.run("sudo make && sudo make install", shell=True)
        Logger.info("[INFO] Python3升级完成")
        subprocess.run("ln -s /usr/python3.7/bin/python3 /usr/bin/python3", shell=True)

    def set_wifi(self):
        return super().set_wifi()


# 树莓派
class DebianService(BaseService):
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


class Install:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-w-p-s-h", ["help", "pv", "hv", "cps", "cas", "uh", "ih", "has", "im",
                                                              "rh", "phl", "up", "ush", "sh", "sth", "id", "uup"])
        service = DebianService()
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
            elif opt == "--uup":
                ubuntuservice.upgrade_python3()
    except getopt.GetoptError:
        Logger.error("[ERROR] 没有这个选项, 请使用-h或--help查看可用选项")


if __name__ == '__main__':
    try:
        Install()
    except PermissionError:
        Logger.error("[ERROR] 权限不足,请使用sudo权限运行此程序")
