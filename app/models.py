from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class DeviceHeaders(BaseModel):
    id: str = Field(..., description="Device MAC address")
    access_token: str = Field(..., alias="Access-Token")
    refresh_rate: Optional[int] = Field(None, alias="Refresh-Rate")
    battery_voltage: Optional[float] = Field(None, alias="Battery-Voltage")
    fw_version: Optional[str] = Field(None, alias="FW-Version")
    rssi: Optional[int] = Field(None, alias="RSSI")
    width: Optional[int] = Field(800, alias="Width")
    height: Optional[int] = Field(480, alias="Height")


class SetupHeaders(BaseModel):
    id: str = Field(..., description="Device MAC address")
    fw_version: Optional[str] = Field(None, alias="FW-Version")


class DisplayResponse(BaseModel):
    status: int = 0
    image_url: str
    filename: str
    refresh_rate: int = 1800
    update_firmware: bool = False
    firmware_url: Optional[str] = None
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
    battery_voltage: Optional[float] = None
    heap_free: Optional[int] = None
    rssi: Optional[int] = None
    wake_reason: Optional[str] = None
    sleep_duration: Optional[int] = None
    firmware_version: Optional[str] = None
    uptime: Optional[int] = None
    wifi_connect_time: Optional[int] = None
    image_download_time: Optional[int] = None
    display_render_time: Optional[int] = None


class ScreenRequest(BaseModel):
    content_type: Literal["html", "uri", "data"]
    content: str
    filename: Optional[str] = None
    width: int = 800
    height: int = 480
    device_id: Optional[str] = None


class ScreenResponse(BaseModel):
    status: str = "success"
    image_url: str
    filename: str


class Device(BaseModel):
    mac_address: str
    api_key: str
    friendly_id: str
    created_at: datetime
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    battery_voltage: Optional[float] = None


class ErrorResponse(BaseModel):
    status: int
    error: str
    message: str
    retry_after: Optional[int] = None