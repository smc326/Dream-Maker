import hashlib
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from urllib.parse import urlparse

import aiohttp

from .device import DreamDevice

_LOGGER = logging.getLogger(__name__)

CLIENT_ID = 'upluszhushou'
CLIENT_SECRET = 'eZOQScs1pjXyzs'
APP_ID = 'MB-SYJCSGJYY-0000'
APP_KEY = '64ad7e690287d740f6ed00924264e3d9'
UHONE_CLIENT_ID = '956877020056553-08002700DC94'
app_name = 'dm_app'
auth_key = 'd6af55159aa125fd'

TOKEN_API = 'https://api.dream-maker.com:8444/APIServerV2/user/account'
GET_DEVICES_API = 'https://api.dream-maker.com:8444/APIServerV2/room/list?creatorOnly=false'
GET_DEVICE_NET_QUALITY_API = 'https://api.dream-maker.com:8444/APIServerV2/room/info/{}'
GET_DEVICE_LAST_REPORT_STATUS_API = 'https://api.dream-maker.com:8444/APIServerV2/room/info/{}'
SEND_COMMAND_API = 'https://api.dream-maker.com:8444/APIServerV2/control/product/{}000000/device/{}'
SEND_MANUAL_COMMAND_API = 'https://api.dream-maker.com:8444/APIServerV2/control/manual/product/{}000000/device/{}'
GET_HARDWARE_CONFIG_API = 'https://api.dream-maker.com:8444/APIServerV2/room/info/{}'


class TokenHolder(ABC):

    @abstractmethod
    async def async_get(self) -> (str, datetime):
        pass

    @abstractmethod
    async def async_set(self, token: str, created_at: datetime):
        pass


class MemoryTokenHolder(TokenHolder, ABC):

    def __init__(self, next_token_holder: TokenHolder = None):
        self._token = None
        self._created_at = None
        self._next_token_holder = next_token_holder
        self._next_token_holder_loaded = False

    async def async_get(self) -> (str, datetime):
        if self._next_token_holder and not self._next_token_holder_loaded:
            token, created_at = await self._next_token_holder.async_get()
            self._token = token
            self._created_at = created_at
            self._next_token_holder_loaded = True

        return self._token, self._created_at

    async def async_set(self, token: str, created_at: datetime):
        self._token = token
        self._created_at = created_at

        if self._next_token_holder:
            await self._next_token_holder.async_set(token, created_at)


class DreamClientException(Exception):
    pass


class DreamClient:

    def __init__(self, username: str, password: str, token_holder: TokenHolder = None):
        self._username = username
        self._password = password
        self._token_holder = MemoryTokenHolder(token_holder)

    async def try_login(self) -> str:
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent':'okhttp/4.11.0',
            'Dm-Phone-Type': 'android',
            'Dm-App-Version': '1.6.2'
        }
        params = {
            'telephone': self._username,
            'password_md5': hashlib.md5(self._password.encode('utf-8')).hexdigest()[8:-8],
            'app_name': app_name,
            'auth_key': auth_key
        }
        #_LOGGER.debug('try_login获取登入data{}'.format(params))
        async with aiohttp.ClientSession() as session:
            async with session.get(url=TOKEN_API, params=params, headers=headers) as response:
                content = await response.json()
                
                if 'msg' in content and content['msg'] != 'OK':
                    raise DreamClientException(content['msg'])

                #_LOGGER.debug('try_login获取token{}'.format(content))
                app_key = content['data']['app_key']
                #_LOGGER.debug('try_login获取token{}'.format(app_key))
                return content['data']['app_key']

    async def get_token(self):
        token, created_at = await self._token_holder.async_get()
        # 未登录或9天后自动重新登录
        if token is None or (datetime.now() - created_at).days >= 9:
            token = await self.try_login()
            #_LOGGER.debug('get_token获取token{}'.format(token))
            await self._token_holder.async_set(token, datetime.now())

        return token

    async def get_devices(self) -> List[DreamDevice]:
        """
        获取设备列表
        """
        headers = await self._generate_common_headers(GET_DEVICES_API)
        #_LOGGER.debug('get_devices获取token{}'.format(headers))

        async with aiohttp.ClientSession() as http_client:
            async with http_client.get(url=GET_DEVICES_API, headers=headers) as response:
                content = await response.json(content_type=None)
                #_LOGGER.debug('get_devices获取token{}'.format(content))

                self._assert_response_successful(content)
                

                devices = []
                for raw in content['data']:
                    #_LOGGER.debug('Device Info: {}'.format(raw))
                    device = DreamDevice(self, raw)
                    await device.async_init()
                    devices.append(device)

                return devices

    async def get_net_quality_by_device(self, id: str):
        """
        获取新风机参数
        """
        url = GET_DEVICE_NET_QUALITY_API.format(id)
        headers = await self._generate_common_headers(url)

        async with aiohttp.ClientSession() as http_client:
            async with http_client.get(url=url, headers=headers) as response:
                content = await response.json(content_type=None)
                self._assert_response_successful(content)

                return content['data']['new_air_status']
            
    async def get_senser_by_device(self, id: str):
        """
        获取贝贝空气参数
        """
        url = GET_DEVICE_NET_QUALITY_API.format(id)
        headers = await self._generate_common_headers(url)

        async with aiohttp.ClientSession() as http_client:
            async with http_client.get(url=url, headers=headers) as response:
                content = await response.json(content_type=None)
                self._assert_response_successful(content)

                return content['data']['checker_status']
            
    async def get_last_report_status_by_device(self, id: str):
        """
        获取设备最新状态
        """
        url = GET_DEVICE_LAST_REPORT_STATUS_API.format(id)
        headers = await self._generate_common_headers(url)

        async with aiohttp.ClientSession() as http_client:
            async with http_client.get(url=url, headers=headers) as response:
                content = await response.json(content_type=None)
                self._assert_response_successful(content)
                #_LOGGER.debug('get_last_report_status_by_device获取content{}'.format(content))
                data = {
                    
                    'checker_aqi_out' : content['data']['checker_status']['aqi'],
                    'checker_aqi_out_desc' : content['data']['checker_status']['aqi_desc'],
                    'checker_pm25_out' : content['data']['checker_status']['pm25_out'],
                    'checker_pm25_out_desc' : content['data']['checker_status']['pm25_out_desc'],
                    'checker_status_co2' : content['data']['checker_status']['status']['co2'],
                    'checker_status_co2_desc' : content['data']['checker_status']['status']['co2_desc'],
                    'checker_status_pm1' : content['data']['checker_status']['status']['pm1'] if 'pm1' in content['data']['checker_status']['status'] else None,
                    'checker_status_pm10' : content['data']['checker_status']['status']['pm10'] if 'pm10' in content['data']['checker_status']['status'] else None,
                    'checker_status_pm25' : content['data']['checker_status']['status']['pm25'],
                    'checker_status_pm25_desc' : content['data']['checker_status']['status']['pm25_desc'],
                    'checker_status_temp' : content['data']['checker_status']['status']['temp'],
                    'checker_status_Humi' : content['data']['checker_status']['status']['rh'],
                    'temp_out' : content['data']['new_air_status']['status']['temp_out'],
                    'air_hour' : content['data']['new_air_status']['status']['air_hour'] if 'air_hour' in content['data']['new_air_status']['status'] else None,
                    'fanspeed' : content['data']['new_air_status']['status']['fanspeed'] if 'fanspeed' in content['data']['new_air_status']['status'] else None,
                    'heating' : content['data']['new_air_status']['status']['ext1'],
                    'power' : content['data']['new_air_status']['status']['power'],
                    'sleep' : content['data']['new_air_status']['status']['sleep']

                }
                _LOGGER.debug('get_last_report_status_by_device获取content{}'.format(data))
                
                #循环添加耗材参数
                for item in content['data']['new_air_status']['filter']:
                   data.update({item['type']: item['left']})

                _LOGGER.debug('get_last_report_status_by_device获取content{}'.format(data))


                if 'air_hour' in content['data']['new_air_status']['status']:
                    data['air_hour'] = content['data']['new_air_status']['status']['air_hour']
                else:
                    data.pop('air_hour', None)

                if 'fanspeed' in content['data']['new_air_status']['status']:
                    data['fanspeed'] = content['data']['new_air_status']['status']['fanspeed']
                else:
                    data.pop('fanspeed', None)

                if 'pm1' in content['data']['checker_status']['status']:
                    data['checker_status_pm1'] = content['data']['checker_status']['status']['pm1']
                else:
                    data.pop('checker_status_pm1', None)

                if 'pm10' in content['data']['checker_status']['status']:
                    data['checker_status_pm10'] = content['data']['checker_status']['status']['pm10']
                else:
                    data.pop('checker_status_pm10', None)

                #_LOGGER.debug('get_last_report_status_by_device获取content{}'.format(data))
                return data

    async def send_command(self, device_id: str, args: dict):
        url = SEND_COMMAND_API.format(device_id)

        sn = time.strftime('%Y%m%d%H%M%S') + str(random.randint(100000, 999999))
        payload = {
            'sn': sn,
            'cmdMsgList': [{
                'deviceId': device_id,
                'index': 0,
                'cmdArgs': args,
                'subSn': sn + ':0'
            }]
        }

        headers = await self._generate_common_headers(url, json.dumps(payload))

        async with aiohttp.ClientSession() as http_client:
            async with http_client.post(url=url, headers=headers, json=payload) as response:
                content = await response.json(content_type=None)
                self._assert_response_successful(content)

    async def get_hardware_configx(self, wifi_type: str):
        url = GET_HARDWARE_CONFIG_API.format(wifi_type)
        
        async with aiohttp.ClientSession() as http_client:
            async with http_client.get(url=url) as response:
                content = await response.json(content_type=None)

                if 'data' not in content or content['data'] is None or 'url' not in content['data']:
                    _LOGGER.error(
                        '获取配置信息失败, wifi_type: {}, response: {}'.format(wifi_type, json.dumps(content)))
                    raise DreamClientException('获取配置文件失败')

                async with http_client.get(url=content['data']['url']) as config_resp:
                    return await config_resp.json(content_type=None)

    async def get_hardware_config(self, id: str):

        config_resp = '[{"name":"checker_aqi_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"None","k":null,"c":null},"description":"室外空气指数","defaultValue":null},{"name":"checker_aqi_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室外空气质量","defaultValue":null},{"name":"checker_pm25_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"999","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室外PM2.5","defaultValue":null},{"name":"checker_pm25_out_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室外PM2.5质量","defaultValue":null},{"name":"checker_status_co2","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"ppm","k":null,"c":null},"description":"室内二氧化碳浓度","defaultValue":null},{"name":"checker_status_co2_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"空气清新"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室内空气新鲜程度","defaultValue":null},{"name":"checker_status_pm1","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM1浓度","defaultValue":null},{"name":"checker_status_pm10","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM10浓度","defaultValue":null},{"name":"checker_status_pm25","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"0","maxValue":"500","step":"1","unit":"µg/m³","k":null,"c":null},"description":"室内PM25浓度","defaultValue":null},{"name":"checker_status_pm25_desc","type":"enum","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"优"},{"stdValue":2,"description":"良"},{"stdValue":3,"description":"低"}],"description":"室内PM25质量","defaultValue":null},{"name":"checker_status_temp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室内温度","defaultValue":null},{"name":"checker_status_Humi","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"室内湿度","defaultValue":null},{"name":"checker_status_temp_out","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":"-64","maxValue":"191","step":"1","unit":"℃","k":null,"c":null},"description":"室外温度","defaultValue":null},{"name":"air_hour","type":"int","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":{"minValue":"60","maxValue":"220","step":"1","unit":"m³/h","k":null,"c":null},"description":"风量","defaultValue":null},{"name":"fanspeed","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":0},{"stdValue":10,"description":10},{"stdValue":30,"description":30},{"stdValue":50,"description":50}],"description":"风速","defaultValue":null},{"name":"heating","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"低于8℃开启"},{"stdValue":1,"description":"始终开启"},{"stdValue":2,"description":"关闭"},{"stdValue":4,"description":"低于10℃开启"},{"stdValue":5,"description":"低于18℃开启"},{"stdValue":6,"description":"关闭"}],"description":"制热","defaultValue":null},{"name":"power","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":0,"description":"关机"},{"stdValue":1,"description":"开机"}],"description":"电源","defaultValue":null},{"name":"sleep","type":"enum","readable":true,"writable":true,"writeType":null,"attrLabel":null,"variants":[{"stdValue":1,"description":"睡眠"},{"stdValue":2,"description":"手动"},{"stdValue":3,"description":"自动"}],"description":"工作模式","defaultValue":null},{"name":"filter_coarse","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"初效滤网","defaultValue":null},{"name":"filter_medium","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"中效滤网","defaultValue":null},{"name":"filter_high","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"高效滤网","defaultValue":null},{"name":"filter_gas","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"二合一滤网","defaultValue":null},{"name":"filter_pre","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"预过滤钢丝网","defaultValue":null},{"name":"filter_coarse_g02","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"初效钢丝网","defaultValue":null},{"name":"esp","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"ESP集尘装置","defaultValue":null},{"name":"esp_lzn","type":"int","readable":true,"writable":false,"writeType":null,"attrLabel":null,"variants":{"minValue":0,"maxValue":100,"step":1,"unit":"%"},"description":"离子能集尘装置","defaultValue":null}]'
        return json.loads(config_resp)
                
    async def get_device_specs_v2(self, device: DreamDevice) -> List[dict]:
        """
        获取设备配置文件
        :param device:
        :return:
        """
        url = 'https://zj.haier.net/omsappapi/resource/conf/list'
        payload = {
            'deviceType': device.type,
            'model': device.product_name,
            'prodNo': device.product_code,
            'resType': 'config',
            'typeId': device.wifi_type
        }

        headers = await self._generate_common_headers(url, json.dumps(payload), True)

        async with aiohttp.ClientSession() as http_client:
            async with http_client.post(url=url, headers=headers, json=payload) as response:
                content = await response.json(content_type=None)

                if 'data' not in content \
                        or content['data'] is None \
                        or 'resource' not in content['data'] \
                        or not isinstance(content['data']['resource'], list) \
                        or len(content['data']['resource']) == 0:
                    _LOGGER.error('Device[{}]获取配置信息失败, response: {}'.format(device.id, json.dumps(content)))
                    return None

                async with http_client.get(url=content['data']['resource'][0]['resUrl']) as resp:
                    return json.loads(await resp.text()[64:])['baseInfo']['attributes']

    async def _generate_common_headers(self, api, body='', skip_token=False):

        return {
            'Accept-Encoding': 'gzip',
            'User-Agent':'okhttp/4.11.0',
            'app_key': await self.get_token(),
            'Dm-Phone-Type': 'android',
            'Dm-App-Version': '1.6.2'
        }

    @staticmethod
    def _assert_response_successful(resp):
        if 'code' in resp and resp['code'] == '0':
            raise DreamClientException(resp['msg'])

