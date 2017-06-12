# KingCoin v0.0.1

这是一个完全参照Bitcoin v0.1 源码，使用Python语言完全重新实现了一边的项目。

这个项目的目的是为了深刻了解Bitcoin系统的运作机制，并探究与思考其背后的区块链技术的伟大与不足。

同时这个项目仅仅用于实验，目的是为了探索Bitcoin系统的运行细节，同时也是将来开展论文研究的实验平台。

![img1](imgs\img1.png)

## 运行方法

### 基本环境

* python 2.7 (不支持python3)
* 对python2.7提供Enum支持的包```pip install enum34  ```
* python hashlib ```pip install hashlib``` (或者是 ```easy_install hashlib```) (Windows需要安装python编译包)
* wxpython https://wxpython.org/
* openssl  区分windows和linux平台

### Windows

对于Windows来说项目```libs```目录下已经提供的 Openssl 的 dll 库，故不需要在Windows平台上安装编译Openssl

但是 对于 Windows Python 来说， 需要提供能供安装 hashlib的环境Microsoft Visual C++ Compiler for Python 2.7：

https://www.microsoft.com/en-us/download/details.aspx?id=44266

### Linux

linux 需要具有Openssl 库

### 运行

在项目根目录下找到run.py

```shell
python run.py
```

即可运行项目。

## 其他

目前项目还比较粗糙，里面充斥着大量的不合理写法与错误设计，及大量无用注释。最近比较繁忙，请谅解。