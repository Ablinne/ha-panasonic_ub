"""Panasonic UB Blu-ray Integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_AUTH_ENABLE,
    CONF_KEY,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)
from .coordinator import PanasonicUBCoordinator
from .panasonic_api import PanasonicSecureAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["media_player"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Extract configuration
    # Note: OptionsFlow now updates entry.data directly, so we primarily read from there.
    host = entry.data[CONF_HOST]
    key = entry.data.get(CONF_KEY, "")
    mac = entry.data.get(CONF_MAC)
    auth_enable = entry.data.get(CONF_AUTH_ENABLE, True)
    poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    session = async_get_clientsession(hass)

    # Initialize API
    try:
        api = PanasonicSecureAPI(
            host, key, session, mac_address=mac, auth_enabled=auth_enable
        )
    except ValueError as err:
        _LOGGER.error("Configuration Error: %s", err)
        return False

    # Initialize Coordinator
    coordinator = PanasonicUBCoordinator(hass, api, poll_interval)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for updates
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
