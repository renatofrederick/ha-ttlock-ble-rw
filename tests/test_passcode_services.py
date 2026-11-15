"""Tests for explicit, validated passcode mutation services."""

from __future__ import annotations

import pytest
import voluptuous as vol
from ttlock_ble import KeyboardPwdType, PasscodeEntry

from custom_components.ttlock_ble.const import DOMAIN


def _lock_entity(hass) -> str:
    return hass.states.async_all("lock")[0].entity_id


async def test_add_passcode_calls_only_selected_connection(
    hass, setup_integration, mock_ttlock_connection
) -> None:
    await hass.services.async_call(
        DOMAIN,
        "add_passcode",
        {
            "entity_id": _lock_entity(hass),
            "code": "1234",
            "pwd_type": "PERIOD",
            "start_date": "2601010000",
            "end_date": "2612312359",
        },
        blocking=True,
    )
    mock_ttlock_connection.async_add_passcode.assert_awaited_once()
    call = mock_ttlock_connection.async_add_passcode.await_args
    assert call.args == ("1234",)
    assert call.kwargs["start_date"] == "2601010000"
    assert call.kwargs["end_date"] == "2612312359"


async def test_delete_passcode_rejects_invalid_pin_before_ble(
    hass, setup_integration, mock_ttlock_connection
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN,
            "delete_passcode",
            {"entity_id": _lock_entity(hass), "code": "12"},
            blocking=True,
        )
    mock_ttlock_connection.async_delete_passcode.assert_not_awaited()


async def test_get_passcodes_returns_sensitive_service_response(
    hass, setup_integration, mock_ttlock_connection
) -> None:
    mock_ttlock_connection.async_get_passcodes.return_value = [
        PasscodeEntry(
            passcode="123456",
            pwd_type=KeyboardPwdType.PERMANENT,
            start_date=None,
            end_date=None,
            cyclic_schedule=None,
        )
    ]
    response = await hass.services.async_call(
        DOMAIN,
        "get_passcodes",
        {"entity_id": _lock_entity(hass)},
        blocking=True,
        return_response=True,
    )
    assert response == {
        "passcodes": [
            {
                "code": "123456",
                "pwd_type": "PERMANENT",
                "start_date": None,
                "end_date": None,
            }
        ]
    }
