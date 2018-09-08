# HomeAssistant Service Install Script for Raspberry Pi

## 使用说明
将此文件放入任意路径下,使用sudo执行

或使用`sudo nano install.py`然后将内容复制进去
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
