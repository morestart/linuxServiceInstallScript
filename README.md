# HomeAssistant Service Install Script

## 使用说明
将此文件放入任意路径下,使用sudo执行

或使用`sudo nano install.py`然后将内容复制进去
## 参数说明
- `-wifi`添加wifi配置
- `-version` 查看版本号
- `-source` 更换pip apt源
- `-prepare` 更新软件源与软件
- `-installHA` 安装HomeAssistant
- `-autostart` 添加自启动
- `-samba` 安装并配置samba
- `-chinese` 中文配置
- `-mosquitto` MQTT Broker安装


## 示例

`sudo python3 install.py -wifi -version`
