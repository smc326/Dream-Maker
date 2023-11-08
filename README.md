# Dream-Maker
Dream Maker fresh air system Custom components for Homeassistant

全部代码从banto6/haier代码修改而来，小白一枚，也不知道怎么通知这位大神，在此感谢banto6。

代码根据haier的api接口进行修改，由于本人只有两款zeico_1.0.0和3.0.0的设备，他俩带的贝贝空气是1.0.0和2.0.0的；再加上用早期v2版本接口的手机软件”造梦者新风“，其中的room方式获取传感器比较方便，便没有用造梦者+APP所使用的v3版本API；

此代码暂时只能支持zeico_1.0.0和3.0.0版本的设备，参数项全部硬改为haier的参数格式，并把造梦者的数据结构改造成haier的结构，所有其中可能很多看起来很尴尬的程序写法；

现在只改了传感器方面的代码，控制部分不太需要，还没着手去修改；

如果有其他版本的设备，可以联系我wx：smc326

## 已支持实体

- Select（暂时没改控制部分代码）
- Sensor
- Binary Sensor


## 安装

方法1：下载并复制`custom_components/haier`文件夹到HomeAssistant根目录下的`custom_components`文件夹即可完成安装

方法2：已经安装了HACS，可以点击按钮快速安装 [![通过HACS添加集成](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=smc326&repository=dream_maker&category=integration)

## 配置

配置 > 设备与服务 >  集成 >  添加集成 > 搜索`Dream Maker`

或者点击: [![添加集成](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=dream_maker)

## 调试
在`configuration.yaml`中加入以下配置来打开调试日志。

```yaml
logger:
  default: warn
  logs:
    custom_components.dream_maker: debug
```
