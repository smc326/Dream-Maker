import json
import logging
from typing import List

from .attribute import DreamAttribute, V1SpecAttributeParser

_LOGGER = logging.getLogger(__name__)


class DreamDevice:
    _raw_data: dict
    _sw_version: str
    _attributes: List[DreamAttribute]

    def __init__(self, client, raw: dict):
        self._client = client
        self._raw_data = raw
        self._sw_version = None
        self._attributes = []

    @property
    def id(self):
        return self._raw_data['room_id']

    @property
    def device_id(self):
        return self._raw_data['new_air']['device_id']

    @property
    def name(self):
        return self._raw_data['new_air']['nickname']

    @property
    def type(self):
        return self._raw_data['new_air']['product_type']
    
    @property
    def product_code(self): 
        return self._raw_data['new_air']['product_id']

    @property
    def product_name(self):
        return self._product_name

    @property
    def wifi_type(self):
        return self._raw_data['new_air']['is_online']

    @property
    def checker_id(self):
        return self._raw_data['checker']['device_id']

    @property
    def checker_name(self):
        return self._raw_data['checker']['nickname']

    @property
    def checker_product_id(self):
        return self._raw_data['checker']['product_id']
    
    @property
    def checker_protocol(self):
        return self._checker_protocol

    @property
    def checker_product_model(self):
        return self._product_name

    @property
    def is_virtual(self):
        return 'virtual' in self._raw_data and self._raw_data['virtual']

    @property
    def sw_version(self):
        return self._sw_version

    @property
    def attributes(self) -> List[DreamAttribute]:
        return self._attributes

    async def async_init(self):
        # 获取sw_version
        if self.is_virtual:
            self._sw_version = 'unknown'
        else:
            net = await self._client.get_net_quality_by_device(self.id)
            sensor = await self._client.get_senser_by_device(self.id)
            self._sw_version = net['protocol'] if 'protocol' in net else 'unknown'
            self._product_name = net['product_model'] if 'product_model' in net else 'unknown'
            self._checker_protocol = sensor['protocol'] if 'protocol' in net else 'unknown'



        # 解析Attribute
        # noinspection PyBroadException
        try:
            parser = V1SpecAttributeParser()
            left_party = '['
            right_party = ']'
            mid_party = ','
            zeico_sensor = ''
            zeico_air = ''
            _LOGGER.debug('获取config_resp{}'.format(self.checker_protocol))
            _LOGGER.debug('获取config_resp{}'.format(self.sw_version))

            if self._checker_protocol == 'zeico_2.0.0':
                zeico_sensor = '{"name":"checker_aqi_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"None","k":null,"c":null},"description":"室外空气指数","defaultValue":null},{"name":"checker_aqi_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"轻度"}],"description":"室外空气质量","defaultValue":null},{"name":"checker_pm25_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"999","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室外PM2.5","defaultValue":null},{"name":"checker_pm25_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"轻度"}],"description":"室外PM2.5质量","defaultValue":null},{"name":"checker_status_co2","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"ppm","k":null,"c":null},"description":"室内二氧化碳浓度","defaultValue":null},{"name":"checker_status_co2_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"空气清新"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"空气浑浊"}],"description":"室内空气新鲜程度","defaultValue":null},{"name":"checker_status_pm1","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM1浓度","defaultValue":null},{"name":"checker_status_pm10","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM10浓度","defaultValue":null},{"name":"checker_status_pm25","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM2.5浓度","defaultValue":null},{"name":"checker_status_pm25_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"轻度"}],"description":"室内PM2.5质量","defaultValue":null},{"name":"checker_status_temp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室内温度","defaultValue":null},{"name":"temp_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室外温度","defaultValue":null},{"name":"checker_status_Humi","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"室内湿度","defaultValue":null}'


            if self._checker_protocol == 'zeico_1.0.0':
                zeico_sensor = '{"name":"checker_aqi_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"None","k":null,"c":null},"description":"室外空气指数","defaultValue":null},{"name":"checker_aqi_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"轻度"}],"description":"室外空气质量","defaultValue":null},{"name":"checker_pm25_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"999","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室外PM2.5","defaultValue":null},{"name":"checker_pm25_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"轻度"}],"description":"室外PM2.5质量","defaultValue":null},{"name":"checker_status_co2","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"ppm","k":null,"c":null},"description":"室内二氧化碳浓度","defaultValue":null},{"name":"checker_status_co2_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"空气清新"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"空气浑浊"}],"description":"室内空气新鲜程度","defaultValue":null},{"name":"checker_status_pm25","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM2.5浓度","defaultValue":null},{"name":"checker_status_pm25_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"},{"stdValue":4,"description":"轻度"}],"description":"室内PM2.5质量","defaultValue":null},{"name":"checker_status_temp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室内温度","defaultValue":null},{"name":"temp_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室外温度","defaultValue":null},{"name":"checker_status_Humi","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"室内湿度","defaultValue":null}'


            if self._sw_version == 'zeico_3.0.0':
                zeico_air = '{"name":"air_hour","type":"int","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"220","step":"1","unit":"m³/h","k":null,"c":null},"description":"风量","defaultValue":null},{"name":"fanspeed","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":50,"step":1,"unit":"Hz"},"description":"风速","defaultValue":null},{"name":"heating","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":4,"description":"低于10℃开启"},{"stdValue":5,"description":"低于18℃开启"},{"stdValue":6,"description":"关闭"}],"description":"制热","defaultValue":null},{"name":"power","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"关机"},{"stdValue":1,"description":"开机"}],"description":"电源","defaultValue":null},{"name":"sleep","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"睡眠"},{"stdValue":2,"description":"手动"},{"stdValue":3,"description":"自动"}],"description":"工作模式","defaultValue":null},{"name":"filter_coarse_g02","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"初效钢丝网","defaultValue":null},{"name":"filter_medium","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"中效滤网","defaultValue":null},{"name":"filter_high","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"高效滤网","defaultValue":null},{"name":"esp_lzn","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"离子能集尘装置","defaultValue":null}'


            if self._sw_version == 'zeico_1.0.0':
                zeico_air = '{"name":"fanspeed","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":0},{"stdValue":10,"description":10},{"stdValue":30,"description":30},{"stdValue":50,"description":50}],"description":"风速","defaultValue":null},{"name":"heating","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"低于8℃开启"},{"stdValue":1,"description":"始终开启"},{"stdValue":2,"description":"关闭"}],"description":"制热","defaultValue":null},{"name":"power","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"关机"},{"stdValue":1,"description":"开机"}],"description":"电源","defaultValue":null},{"name":"sleep","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"睡眠"},{"stdValue":2,"description":"手动"},{"stdValue":3,"description":"自动"}],"description":"工作模式","defaultValue":null},{"name":"filter_coarse","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"初效滤网","defaultValue":null},{"name":"filter_medium","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"中效滤网","defaultValue":null},{"name":"filter_high","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"高效滤网","defaultValue":null},{"name":"filter_gas","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"二合一滤网","defaultValue":null},{"name":"filter_pre","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"预过滤钢丝网","defaultValue":null},{"name":"esp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"ESP集尘装置","defaultValue":null}'
        

            _LOGGER.debug('获取{}'.format(zeico_sensor))
            _LOGGER.debug('获取{}'.format(zeico_air))

            if zeico_sensor == '':
                config_resp = left_party + zeico_air + right_party
            else:
                config_resp = left_party + zeico_sensor + mid_party + zeico_air + right_party

            _LOGGER.debug('已从HomeAssistant加载到缓存的token{}'.format(config_resp))
            #config_resp = '[{"name":"checker_aqi_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"None","k":null,"c":null},"description":"室外空气指数","defaultValue":null},{"name":"checker_aqi_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室外空气质量","defaultValue":null},{"name":"checker_pm25_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"999","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室外PM2.5","defaultValue":null},{"name":"checker_pm25_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室外PM2.5质量","defaultValue":null},{"name":"checker_status_co2","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"ppm","k":null,"c":null},"description":"室内二氧化碳浓度","defaultValue":null},{"name":"checker_status_co2_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"空气清新"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室内空气新鲜程度","defaultValue":null},{"name":"checker_status_pm1","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM1浓度","defaultValue":null},{"name":"checker_status_pm10","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM10浓度","defaultValue":null},{"name":"checker_status_pm25","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM25浓度","defaultValue":null},{"name":"checker_status_pm25_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室内PM25质量","defaultValue":null},{"name":"checker_status_temp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室内温度","defaultValue":null},{"name":"checker_status_Humi","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"室内湿度","defaultValue":null},{"name":"checker_status_temp_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室外温度","defaultValue":null},{"name":"air_hour","type":"int","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":{"minValue":"60","maxValue":"220","step":"1","unit":"m³/h","k":null,"c":null},"description":"风量","defaultValue":null},{"name":"fanspeed","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":0},{"stdValue":10,"description":10},{"stdValue":30,"description":30},{"stdValue":50,"description":50}],"description":"风速","defaultValue":null},{"name":"heating","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"低于8℃开启"},{"stdValue":1,"description":"始终开启"},{"stdValue":2,"description":"关闭"},{"stdValue":4,"description":"低于10℃开启"},{"stdValue":5,"description":"低于18℃开启"},{"stdValue":6,"description":"关闭"}],"description":"制热","defaultValue":null},{"name":"power","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"关机"},{"stdValue":1,"description":"开机"}],"description":"电源","defaultValue":null},{"name":"sleep","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"睡眠"},{"stdValue":2,"description":"手动"},{"stdValue":3,"description":"自动"}],"description":"工作模式","defaultValue":null},{"name":"filter_coarse","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"初效滤网","defaultValue":null},{"name":"filter_medium","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"中效滤网","defaultValue":null},{"name":"filter_high","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"高效滤网","defaultValue":null},{"name":"filter_gas","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"二合一滤网","defaultValue":null},{"name":"filter_pre","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"预过滤钢丝网","defaultValue":null},{"name":"filter_coarse_g02","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"初效钢丝网","defaultValue":null},{"name":"esp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"ESP集尘装置","defaultValue":null},{"name":"esp_lzn","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"离子能集尘装置","defaultValue":null}]'
            properties = json.loads(config_resp)

            _LOGGER.debug('已从HomeAssistant加载到缓存的token{}'.format(properties))
            #properties = '{"name":"checker_aqi_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","k":null,"c":null},"description":"当前室外空气指数","defaultValue":null},{"name":"checker_aqi_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"当前室外空气质量","defaultValue":null},{"name":"checker_pm25_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"999","step":"1","k":null,"c":null},"description":"室外实时PM2.5","defaultValue":null},{"name":"checker_pm25_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"当前室外PM2.5质量","defaultValue":null},{"name":"checker_status_co2","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","k":null,"c":null},"description":"当前室内二氧化碳浓度","defaultValue":null},{"name":"checker_status_co2_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"空气清新"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"当前室内空气新鲜程度","defaultValue":null},{"name":"checker_status_pm1","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","k":null,"c":null},"description":"当前室内PM1浓度","defaultValue":null},{"name":"checker_status_pm10","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","k":null,"c":null},"description":"当前室内PM10浓度","defaultValue":null},{"name":"checker_status_pm25","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","k":null,"c":null},"description":"当前室内PM25浓度","defaultValue":null},{"name":"checker_status_pm25_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"当前室内PM25质量","defaultValue":null},{"name":"checker_status_temp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室内温度","defaultValue":null},{"name":"checker_status_Humi","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"室内湿度","defaultValue":null},{"name":"checker_status_temp_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室外温度","defaultValue":null},{"name":"air_hour","type":"int","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":{"minValue":"60","maxValue":"220","step":"1","unit":"m³/h","k":null,"c":null},"description":"风量","defaultValue":null},{"name":"fanspeed","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":10,"description":10},{"stdValue":30,"description":30},{"stdValue":50,"description":50}],"description":"风量（老款）","defaultValue":null},{"name":"heating","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"低于8℃开启"},{"stdValue":1,"description":"始终开启"},{"stdValue":2,"description":"关闭"},{"stdValue":4,"description":"低于10℃开启"},{"stdValue":5,"description":"低于18℃开启"},{"stdValue":6,"description":"关闭"}],"description":"制热","defaultValue":null},{"name":"power","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"关机"},{"stdValue":1,"description":"开机"}],"description":"电源","defaultValue":null},{"name":"sleep","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"睡眠"},{"stdValue":2,"description":"手动"},{"stdValue":3,"description":"自动"}],"description":"工作模式","defaultValue":null}'
            for item in properties:
               # _LOGGER.debug('已从HomeAssistant加载到缓存的token{}'.format(item))
                attr = parser.parse_attribute(item)
                
                if attr:
                    self._attributes.append(attr)

            iter = parser.parse_global(properties)
            if iter:
                for item in iter:
                    self._attributes.append(item)
        except Exception:
            _LOGGER.exception('获取attributes失败')

    async def write_attributes(self, values):
        await self._client.send_command(self.id, values)

    async def read_attributes(self):
        return await self._client.get_last_report_status_by_device(self.id)

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'wifi_type': self.wifi_type,
            'checker_protocol': self.checker_protocol
        })
