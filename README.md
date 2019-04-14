
项目持续进行中，2019年4月14日完成核心功能的编写，可以将其称之为0.1版本。

原本打算用Flask做一个跨团队的营销项目管理系统，但是工程量太大了，
我自己搞不定。

所以退而求其次，这个应用就叫LEAF
意思是Light Easy Agile File management system
即，【轻简灵的项目文档管理系统】

主要目的是解决跨团队协作中的文档管理和通知的难点。

部署指南（未完成）：

1、 请在项目根目录下自行创建.env和.flaskenv两个文件。
2、请在.env文件中，声明SECRET_KEY, SENDGRID_API_KEY和DB_URI_DEV三个环境变量
3、请创建对应的mysql数据库
4、准备工作都就绪后，在项目根目录运行flask init初始化并生成一个默认的管理员账号


2019年4月14日
Leng Ke
