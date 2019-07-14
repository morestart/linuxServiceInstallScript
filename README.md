# Debian Service Install Script

## 使用说明

执行以下命令下载程序

`sudo curl -O https://raw.githubusercontent.com/morestart/RaspbianInstallScript/chinese/install.py`
## 参数说明
- `-w` 添加wifi配置
- `-p` 更新软件包列表与软件
- `-s` 安装samba服务
- `-h` 显示帮助
- `--help` 显示帮助
- `--pv` 获取当前Python版本
- `--hv` 获取当前HA版本
- `--cps` 更改pip源
- `--cas` 更改apt源
- `--uh` 更新HA
- `--usp` 安装特定版本的HA
- `--ih` 安装最新版HA
- `--has` 配置ha自启动
- `--im` 安装配置mosquitto
- `--rh` 重启HA
- `--phl` 打印HA log
- `--up` 更新Python版本为3.7.2
- `--sh` 运行HA实例
- `--sth` 结束HA的运行


## 示例
以下命令作用:添加wifi配置 安装0.94版本HA 打印HA log

`sudo python3 install.py -w --ih 0.94.0 --phl`

升级Python3版本

`sudo python3 install.py --up`