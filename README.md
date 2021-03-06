# LagouSpider

简单的拉勾网站爬虫程序，提供如下功能：

* 可抓取免费代理网站，反屏蔽
* 使用多线程爬取，提高爬虫效率
* 使用MySql数据库连接池，保障多线程状态下正常提交任务

## 开发环境:
开发工具：pycharm  
python版本：python 3.8.3  
数据库版本：mysql-8.0.20 


## 运行前的配置
* ### Mysql (windows安装说明)
下载mysql(zip包):
<https://dev.mysql.com/downloads/mysql/>  
```text
解压到安装目录：
例如：D:\Softwares\mysql-8.0.20

在安装目录下创建my.ini配置文件，配置以下信息：
[mysql]  
# 设置 mysql 客户端默认字符集  
default-character-set=utf8 
 
[mysqld]  
#设置 3306 端口  
port = 3306  

# 设置 mysql 的安装目录  
basedir=D:\Softwares\mysql-8.0.20

# 设置 mysql 数据库的数据的存放目录  
datadir=D:\Softwares\mysql-8.0.20\data 

# 允许最大连接数  
max_connections=200  

# 允许连接失败的次数。防止有人从该主机试图攻击数据库系统
max_connect_errors=10

# 服务端使用的字符集默认为 8 比特编码的 latin1 字符集  
character-set-server=utf8  

# 设置mysql客户端默认字符集
default-character-set=utf8

# 创建新表时将使用的默认存储引擎  
default-storage-engine=INNODB

# 默认使用“mysql_native_password”插件认证
default_authentication_plugin=mysql_native_password
————————————————

win+x 以管理员身份打开命令窗口：
打开安装目录下的bin目录：
PS C:\WINDOWS\system32> cd D:\Softwares\mysql-8.0.20
PS D:\Softwares\mysql-8.0.20> cd bin

新建 data 文件夹：发现多了一个 data 文件夹；此时 MySQL 建立了默认的数据库，用户名为 root，密码为空。
\bin>mysqld --initialize-insecure --user=mysql
\bin>mysqld --initialize --console

mysqld -install
第一次安装的话会显示 "Service successfully installed."

++++++++++++++++++++++++++++++
启动mysql服务：
net start mysql 
不管用时，使用下面命令：
mysqld --console
++++++++++++++++++++++++++++++
打开客户端连接：
cd D:\Softwares\mysql-8.0.20
mysql -u root -p
++++++++++++++++++++++++++++++


python环境下连接mysql：
1. 安装mysql-connector 驱动
python -m pip install mysql-connector

2.代码编写，执行下面代码不报错即可：
import mysql.connector
 
mydb = mysql.connector.connect(
  host="localhost",       # 数据库主机地址
  user="yourusername",    # 数据库用户名
  passwd="yourpassword"   # 数据库密码
)
print(mydb)  
```


* ### mysql配置参考链接：
<https://blog.csdn.net/u010505080/article/details/100026611>  
<https://zhuanlan.zhihu.com/p/44977117>  
<https://www.runoob.com/python3/python-mysql-connector.html>



## 运行示例
```python
if __name__ == "__main__":
    spider = LagouSpider()
    spider.main()
```
## 运行结果
<img src="https://github.com/shining160/lagou_spider/blob/master/lagou.png">
<img src="https://github.com/shining160/lagou_spider/blob/master/lagou_data.png">
<img src="https://github.com/shining160/lagou_spider/blob/master/lagou_job.png">

## 待改进
* 配置单独的线程处理代理池的变化，避免频繁抓取代理网站
* 配置程序断点恢复的功能

# Thanks
