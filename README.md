# Linux Service Install Script

## 使用说明
将此文件放入任意路径下,使用sudo执行

## 参数说明
-  -s[--source] 换源
-  -a[--addWifi] 添加WIFI配置
-  -p[--prepare] 更新软件列表
-  -f[--fontPinyin] 安装输入法及中文
-  -sb[--samba] 安装samba服务
-  -m[--mosquitto] 安装mqtt broker
-  -at[--autostart] 设置自启动

## 示例

`python3 install.py -s -a -p -f -sb -m -at`
