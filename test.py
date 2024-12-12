"""
# Author: Pratik Gawde, Pranita Shewale
# Date: 11 Nov, 2024
# PROJECT 02
# Description: test file for thermalComfortDashboard
"""

import pytest

from Sensor import *

def test_exception():
    """
    this testcase checks if SensorError exception is raised when invalid portname is passed
    """
    with pytest.raises(SensorError):
        obj = Sensor("dummyPortName")

def test_crc():
    """
    this test case checks if sensors readings were received correctly on I2C
    """
    assert Sensor.check_crc(data=0xbeef,crc_received=0x92)is True

def test_co2Extraction():
    """
    this test case checks if readings are calculated and extracted correctly from modbus registers
    """
    co2,_,_=Sensor.extractReadings([500, 51, 26215, 162, 24249, 60])
    assert co2 is 500

def test_humidityExtraction():
    """
    this test case checks if humidity is extracted correctly from modbus registers
    """
    _,_,h=Sensor.extractReadings([500, 51, 26215, 162, 24249, 60])
    assert h >= 37
def test_temperatureExtraction():
    """
    this test case checks if temperature is extracted correctly from modbus registers
    """
    _,t,_=Sensor.extractReadings([500, 51, 26215, 162, 24249, 60])
    assert t >= 25