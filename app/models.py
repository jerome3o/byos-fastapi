from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DeviceHeaders(BaseModel):
    id: str = Field(..., description="Device MAC address")
    access_token: str = Field(..., alias="Access-Token")
    refresh_rate: int | None = Field(None, alias="Refresh-Rate")
    battery_voltage: float | None = Field(None, alias="Battery-Voltage")
    fw_version: str | None = Field(None, alias="FW-Version")
    rssi: int | None = Field(None, alias="RSSI")
    width: int | None = Field(800, alias="Width")
    height: int | None = Field(480, alias="Height")


class SetupHeaders(BaseModel):
    id: str = Field(..., description="Device MAC address")
    fw_version: str | None = Field(None, alias="FW-Version")


class DisplayResponse(BaseModel):
    status: int = 0
    image_url: str
    filename: str
    refresh_rate: int = 1800
    update_firmware: bool = False
    firmware_url: str | None = None
    reset_firmware: bool = False
    special_function: str = "sleep"
    image_url_timeout: int = 30


class SetupResponse(BaseModel):
    status: int = 200
    api_key: str
    friendly_id: str
    image_url: str
    message: str = "Welcome to your custom TRMNL server"


class DeviceLog(BaseModel):
    battery_voltage: float | None = None
    heap_free: int | None = None
    rssi: int | None = None
    wake_reason: str | None = None
    sleep_duration: int | None = None
    firmware_version: str | None = None
    uptime: int | None = None
    wifi_connect_time: int | None = None
    image_download_time: int | None = None
    display_render_time: int | None = None


class ScreenRequest(BaseModel):
    content_type: Literal["html", "uri", "data", "big_text"]
    content: str
    filename: str | None = None
    width: int = 800
    height: int = 480
    device_id: str | None = None


class ScreenResponse(BaseModel):
    status: str = "success"
    image_url: str
    filename: str


class Device(BaseModel):
    mac_address: str
    api_key: str
    friendly_id: str
    created_at: datetime
    last_seen: datetime | None = None
    firmware_version: str | None = None
    battery_voltage: float | None = None


class ErrorResponse(BaseModel):
    status: int
    error: str
    message: str
    retry_after: int | None = None
