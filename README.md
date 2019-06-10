# Raspberry Pi Service Install Script

## 使用说明
执行以下命令下载程序

`sudo curl -O https://raw.githubusercontent.com/morestart/RaspbianInstallScript/master/install.py`
## 参数说明
- `-w` 添加wifi配置
- `-p` 更新软件包列表与软件
- `-s` 安装samba服务
- `--pv` 获取当前Python版本
- `--hv` 获取当前HA版本
- `--cps` 更改pip源
- `--cas` 更改apt源
- `--uh` 更新HA
- `--usp` 安装特定版本的HA
- `--ih` 安装最新版HA
- `--has` 配置ha自启动
- `--ifp` 安装中文字体与拼音
- `--im` 安装配置mosquitto
- `--rh` 重启HA
- `--phl` 打印HA log
- `--up` 更新Python版本为3.7.2


## 示例
`sudo python3 install.py -w --ih 0.94.0 --phl`
