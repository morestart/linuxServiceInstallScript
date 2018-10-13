# HomeAssistant Service Install Script for Raspberry Pi

## 使用说明
执行以下命令

`curl -O https://raw.githubusercontent.com/morestart/RaspbianInstallScript/master/install.py`
## 参数说明
- `-w`添加wifi配置
- `-v` 查看版本号
- `-s` 更换pip apt源
- `-p` 更新软件源与软件
- `-i` 安装HomeAssistant
- `-a` 添加自启动
- `-sa` 安装并配置samba
- `-c` 中文配置
- `-m` MQTT Broker安装
- `-u` 更新HomeAssistant版本及其依赖


## 示例

`sudo python3 install.py -w true -s true`

`sudo python3 install.py -w True -s True`
