# Dream-Maker
Dream Maker fresh air system Custom components for Homeassistant


## 已支持实体

- Select
- Sensor
- Binary Sensor


## 安装

方法1：下载并复制`custom_components/haier`文件夹到HomeAssistant根目录下的`custom_components`文件夹即可完成安装

方法2：已经安装了HACS，可以点击按钮快速安装 [![通过HACS添加集成](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=smc326&repository=dream_maker&category=integration)

## 配置

配置 > 设备与服务 >  集成 >  添加集成 > 搜索`haier`

或者点击: [![添加集成](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=dream_maker)

## 调试
在`configuration.yaml`中加入以下配置来打开调试日志。

```yaml
logger:
  default: warn
  logs:
    custom_components.dream_maker: debug
```
