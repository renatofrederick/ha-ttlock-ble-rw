"""Explicit, validated BLE passcode mutation services."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from ttlock_ble import KeyboardPwdType

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .connection import TtlockBleConnection

_DATE = vol.Match(r"^\d{10}$")
_PASSCODE = vol.All(str, vol.Match(r"^\d{4,9}$"))


def _connection_for_lock_entity(
    hass: HomeAssistant, entity_id: str
) -> TtlockBleConnection:
    """Resolve a lock entity to exactly one live TTLock BLE connection."""
    if not entity_id.startswith("lock."):
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="passcode_invalid_entity",
            translation_placeholders={"entity_id": entity_id},
        )
    entity = async_get_entity_registry(hass).async_get(entity_id)
    if entity is None or entity.device_id is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="passcode_device_not_found",
            translation_placeholders={"entity_id": entity_id},
        )
    device = async_get_device_registry(hass).async_get(entity.device_id)
    if device is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="passcode_device_not_found",
            translation_placeholders={"entity_id": entity_id},
        )
    mac = next(
        (identifier for domain, identifier in device.identifiers if domain == DOMAIN),
        None,
    )
    if mac is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="passcode_lock_not_found",
            translation_placeholders={"entity_id": entity_id},
        )
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime_data = getattr(entry, "runtime_data", None)
        connections = getattr(runtime_data, "connections", {})
        for connection_mac, connection in connections.items():
            if connection_mac.lower() == mac.lower():
                return cast("TtlockBleConnection", connection)
    raise HomeAssistantError(
        translation_domain=DOMAIN,
        translation_key="passcode_connection_not_found",
        translation_placeholders={"entity_id": entity_id},
    )


def _pwd_type(value: str) -> KeyboardPwdType:
    """Resolve only SDK-supported password types before touching BLE."""
    try:
        return KeyboardPwdType[value.upper()]
    except KeyError as exc:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="passcode_type_invalid",
        ) from exc


async def async_setup_passcode_services(hass: HomeAssistant) -> None:
    """Register mutation services once for all configured TTLock BLE entries."""
    if hass.services.has_service(DOMAIN, "add_passcode"):
        return

    async def handle_add_passcode(call: ServiceCall) -> None:
        connection = _connection_for_lock_entity(hass, call.data["entity_id"])
        await connection.async_add_passcode(
            call.data["code"],
            pwd_type=_pwd_type(call.data["pwd_type"]),
            start_date=call.data["start_date"],
            end_date=call.data["end_date"],
        )

    async def handle_delete_passcode(call: ServiceCall) -> None:
        connection = _connection_for_lock_entity(hass, call.data["entity_id"])
        await connection.async_delete_passcode(
            call.data["code"], pwd_type=_pwd_type(call.data["pwd_type"])
        )

    base = {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("code"): _PASSCODE,
        vol.Optional("pwd_type", default="PERMANENT"): vol.In(("PERMANENT", "PERIOD")),
    }
    hass.services.async_register(
        DOMAIN,
        "add_passcode",
        handle_add_passcode,
        schema=vol.Schema(
            {
                **base,
                vol.Optional("start_date", default="0001311400"): _DATE,
                vol.Optional("end_date", default="9912311400"): _DATE,
            }
        ),  # type: ignore[arg-type] # HA accepts voluptuous service schemas at runtime.
    )
    hass.services.async_register(
        DOMAIN,
        "delete_passcode",
        handle_delete_passcode,
        schema=vol.Schema(base),  # type: ignore[arg-type] # HA accepts voluptuous service schemas at runtime.
    )
