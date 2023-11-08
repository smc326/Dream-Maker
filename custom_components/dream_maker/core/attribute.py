from abc import abstractmethod, ABC
from typing import List

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, UnitOfTemperature, PERCENTAGE, UnitOfVolume, UnitOfEnergy, UnitOfPrecipitationDepth, UnitOfVolumeFlowRate, UnitOfFrequency, \
    REVOLUTIONS_PER_MINUTE


class DreamAttribute:

    def __init__(self, key: str, display_name: str, platform: Platform, options: dict = {}, ext: dict = {}):
        self._key = key
        self._display_name = display_name
        self._platform = platform
        self._options = options
        self._ext = ext

    @property
    def key(self) -> str:
        return self._key

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def platform(self) -> Platform:
        return self._platform

    @property
    def unit(self) -> str:
        """
        获取数据单位
        :return:
        """
        if '温度' in self.display_name:
            return UnitOfTemperature.CELSIUS

        if '湿度' in self.display_name:
            return PERCENTAGE

        return None

    @property
    def options(self) -> dict:
        return self._options

    @property
    def ext(self) -> dict:
        return self._ext


class DreamAttributeParser(ABC):

    @abstractmethod
    def parse_attribute(self, attribute: dict) -> DreamAttribute:
        pass

    @abstractmethod
    def parse_global(self, attributes: List[dict]):
        pass


class V1SpecAttributeParser(DreamAttributeParser, ABC):

    def parse_attribute(self, attribute: dict) -> DreamAttribute:
        if not attribute['writable'] and attribute['readable']:
            return self._parse_as_sensor(attribute)

        if attribute['writable'] and attribute['type'] in ['int', 'double']:
            return self._parse_as_number(attribute)

        if attribute['writable'] and attribute['type'] in ['enum']:
            return self._parse_as_select(attribute)

        if attribute['writable'] and attribute['type'] in ['bool']:
            return self._parse_as_switch(attribute)

        return None

    def parse_global(self, attributes: List[dict]):
        all_attribute_keys = [attribute['name'] for attribute in attributes]

        # 空调特征字段
        climate_feature_fields = [
            ['targetTemperature', 'operationMode', 'windSpeed'],
            # https://github.com/banto6/haier/issues/53 有空调分左右风区
            ['targetTemperature', 'operationMode', 'windSpeedL', 'windSpeedR']
        ]
        for feature_fields in climate_feature_fields:
            if len(list(set(feature_fields) - set(all_attribute_keys))) == 0:
                yield self._parse_as_climate(attributes, feature_fields)
                break
        # 燃气热水器
        if 'outWaterTemp' in all_attribute_keys and 'inWaterTemp' in all_attribute_keys and 'gasPressure' in all_attribute_keys:
            yield self._parse_as_gas_water_heater(attributes)

    @staticmethod
    def _parse_as_sensor(attribute):
        if attribute['type'] == 'bool':
            return DreamAttribute(attribute['name'], attribute['description'], Platform.BINARY_SENSOR)

        options = {}
        ext = {}
        if attribute['type'] == 'enum':
            value_comparison_table = {}
            for item in attribute['variants']:
                value_comparison_table[str(item['stdValue'])] = item['description']

            options['device_class'] = SensorDeviceClass.ENUM
            options['options'] = list(value_comparison_table.values())
            ext['value_comparison_table'] = value_comparison_table

        if isinstance(attribute['variants'], dict) and 'unit' in attribute['variants']:
            if attribute['variants']['unit'] in ['L']:  # 用水量
                options['device_class'] = SensorDeviceClass.WATER
                options['native_unit_of_measurement'] = UnitOfVolume.LITERS

            elif attribute['variants']['unit'] in ['℃']:  # 温度
                options['device_class'] = SensorDeviceClass.TEMPERATURE
                options['native_unit_of_measurement'] = UnitOfTemperature.CELSIUS

            elif attribute['variants']['unit'] in ['ppm']:  # CO2浓度
                options['device_class'] = SensorDeviceClass.CO2
                options['native_unit_of_measurement'] = attribute['variants']['unit']

            elif attribute['variants']['unit'] in ['m³/h']:  # 风量
                options['device_class'] = SensorDeviceClass.WIND_SPEED
                options['native_unit_of_measurement'] = UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR 

            elif attribute['variants']['unit'] in ['µg/m³'] and 'PM1浓度' in attribute['description']:  # PM1浓度
                options['device_class'] = SensorDeviceClass.PM1	
                options['native_unit_of_measurement'] = attribute['variants']['unit']

            elif attribute['variants']['unit'] in ['µg/m³'] and 'PM2.5' in attribute['description']:  # PM2.5浓度
                options['device_class'] = SensorDeviceClass.PM25	
                options['native_unit_of_measurement'] = attribute['variants']['unit']

            elif attribute['variants']['unit'] in ['µg/m³'] and 'PM10' in attribute['description']:  # PM1浓度
                options['device_class'] = SensorDeviceClass.PM10	
                options['native_unit_of_measurement'] = attribute['variants']['unit']

            elif attribute['variants']['unit'] in ['None']:  # AQI
                options['device_class'] = SensorDeviceClass.AQI

            elif attribute['variants']['unit'] in ['%'] and '湿度' in attribute['description']:
                options['device_class'] = SensorDeviceClass.HUMIDITY
                options['native_unit_of_measurement'] = PERCENTAGE

            elif attribute['variants']['unit'] in ['%'] and '湿度' not in attribute['description']:
                options['native_unit_of_measurement'] = PERCENTAGE

            elif attribute['variants']['unit'] in ['KWh']:  # 用电量
                options['device_class'] = SensorDeviceClass.ENERGY
                options['native_unit_of_measurement'] = UnitOfEnergy.KILO_WATT_HOUR  # kWh

            elif attribute['variants']['unit'] in ['Hz']:  # 风量变频
                options['device_class'] = SensorDeviceClass.FREQUENCY
                options['native_unit_of_measurement'] = UnitOfFrequency.HERTZ  # kWh

            elif attribute['variants']['unit'] in ['h', 'min', 's']:  # 时间
                options['device_class'] = SensorDeviceClass.DURATION
                options['native_unit_of_measurement'] = attribute['variants']['unit']

            elif attribute['variants']['unit'] in ['g', 'kg']:
                options['device_class'] = SensorDeviceClass.WEIGHT
                options['native_unit_of_measurement'] = attribute['variants']['unit']

            elif attribute['variants']['unit'] in ['RPM']:  # 转速
                options['native_unit_of_measurement'] = REVOLUTIONS_PER_MINUTE

        return DreamAttribute(attribute['name'], attribute['description'], Platform.SENSOR, options, ext)

    @staticmethod
    def _parse_as_number(attribute):
        options = {
            'native_min_value': attribute['variants']['minValue'],
            'native_max_value': attribute['variants']['maxValue'],
            'native_step': attribute['variants']['step'],
            'device_class': SensorDeviceClass.WIND_SPEED,
            'native_unit_of_measurement': UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR 
        }

        return DreamAttribute(attribute['name'], attribute['description'], Platform.NUMBER, options)

    @staticmethod
    def _parse_as_select(attribute):
        value_comparison_table = {}
        for item in attribute['variants']:
            value_comparison_table[str(item['stdValue'])] = item['description']
            value_comparison_table[str(item['description'])] = item['stdValue']

        ext = {
            'value_comparison_table': value_comparison_table
        }

        options = {
            'options': [item['description'] for item in attribute['variants']]
        }

        return DreamAttribute(attribute['name'], attribute['description'], Platform.SELECT, options, ext)

    @staticmethod
    def _parse_as_switch(attribute):
        options = {
            'device_class': SwitchDeviceClass.SWITCH
        }

        return DreamAttribute(attribute['name'], attribute['description'], Platform.SWITCH, options)

    @staticmethod
    def _parse_as_climate(attributes: List[dict], feature_fields: List[str]):
        for attr in attributes:
            if attr['name'] == 'targetTemperature':
                target_temperature_attr = attr
                break
        else:
            raise RuntimeError('targetTemperature attr not found')

        options = {
            'min_temp': target_temperature_attr['variants']['minValue'],
            'max_temp': target_temperature_attr['variants']['maxValue'],
            'target_temperature_step': target_temperature_attr['variants']['step']
        }

        ext = {
            'customize': True,
            # 是否存在多个风口
            'exist_multiple_vents': 'windSpeedL' in feature_fields
        }

        return DreamAttribute('climate', 'Climate', Platform.CLIMATE, options, ext)
    
    @staticmethod
    def _parse_as_gas_water_heater(attributes: List[dict]):
        for attr in attributes:
            if attr['name'] == 'targetTemp':
                target_temperature_attr = attr
                break
        else:
            raise RuntimeError('targetTemp attr not found')

        options = {
            'min_temp': target_temperature_attr['variants']['minValue'],
            'max_temp': target_temperature_attr['variants']['maxValue'],
            'target_temperature_step': target_temperature_attr['variants']['step']
        }

        ext = {
            'customize': True,
        }

        return DreamAttribute('gas_water_heater', 'GasWaterHeater', Platform.WATER_HEATER, options, ext)
