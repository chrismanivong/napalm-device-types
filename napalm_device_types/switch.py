"""
Abstract base class for switch drivers.

Usage::

    from napalm_device_types import SwitchDriver

    class CiscoSGDriver(SwitchDriver):
        def get_spanning_tree(self):
            ...
"""

from typing import Dict
from napalm.base import NetworkDriver
from napalm_device_types.models import (
    Dot1XPortDict,
    MACACLDict,
    PoESummaryDict,
    PortChannelDict,
    SpanningTreeDict,
)


class SwitchDriver(NetworkDriver):
    """
    Abstract intermediate driver for Ethernet switches.

    Inherits all standard NAPALM NetworkDriver methods (including
    ``get_vlans()``, ``get_mac_address_table()``) and adds switch-specific
    operations that concrete drivers must implement.
    """

    def get_spanning_tree(self) -> Dict[str, SpanningTreeDict]:
        """
        Returns spanning tree status for each STP instance.

        Keys are STP instance identifiers (e.g. VLAN IDs for PVST,
        ``"MST0"`` for MSTP, or ``"0"`` for a single instance).
        Each value contains:

        * mode (string) - STP variant: ``"STP"``, ``"RSTP"``, ``"MSTP"``, ``"PVST"``
        * root_bridge (bool) - whether this device is the root bridge
        * root_id (string) - root bridge MAC address
        * root_priority (int) - root bridge priority
        * bridge_id (string) - this bridge's MAC address
        * bridge_priority (int) - this bridge's priority
        * interfaces (dict) - per-interface STP state:

            * role (string) - ``"root"``, ``"designated"``, ``"alternate"``, ``"backup"``
            * state (string) - ``"forwarding"``, ``"blocking"``, ``"learning"``, ``"listening"``
            * cost (int) - port path cost
            * port_priority (int) - port priority

        Example::

            {
                "1": {
                    "mode": "RSTP",
                    "root_bridge": False,
                    "root_id": "00:11:22:33:44:55",
                    "root_priority": 4096,
                    "bridge_id": "AA:BB:CC:DD:EE:FF",
                    "bridge_priority": 32768,
                    "interfaces": {
                        "GigabitEthernet0/1": {
                            "role": "root",
                            "state": "forwarding",
                            "cost": 4,
                            "port_priority": 128,
                        },
                        "GigabitEthernet0/2": {
                            "role": "designated",
                            "state": "forwarding",
                            "cost": 4,
                            "port_priority": 128,
                        },
                    },
                }
            }
        """
        raise NotImplementedError

    def get_port_channels(self) -> Dict[str, PortChannelDict]:
        """
        Returns port-channel (LAG) configuration and status.

        Keys are port-channel interface names (e.g. ``"Port-Channel1"``).
        Each value contains:

        * members (list of strings) - names of member interfaces
        * protocol (string) - aggregation protocol: ``"LACP"``, ``"PAgP"``, ``"static"``
        * min_links (int) - minimum number of active members required
        * is_up (bool) - whether the LAG is operationally up

        Example::

            {
                "Port-Channel1": {
                    "members": ["GigabitEthernet0/1", "GigabitEthernet0/2"],
                    "protocol": "LACP",
                    "min_links": 1,
                    "is_up": True,
                }
            }
        """
        raise NotImplementedError

    def get_mac_acl(self) -> Dict[str, MACACLDict]:
        """
        Returns the MAC-address-based access control lists configured per port.

        Keys are interface names.  Each value contains:

        * name (string) - interface name (repeated for convenience)
        * policy (string) - ACL mode:

          * ``"allow"`` – whitelist: only listed MACs may use this port
          * ``"deny"``  – blacklist: listed MACs are blocked
          * ``"disabled"`` – no MAC filtering active

        * entries (list) - ACL entries, each with:

          * mac (string) - MAC address (normalised, colon-separated)
          * action (string) - ``"allow"`` or ``"deny"``
          * description (string) - optional human-readable label

        Example::

            {
                "GigabitEthernet0/1": {
                    "name": "GigabitEthernet0/1",
                    "policy": "allow",
                    "entries": [
                        {"mac": "AA:BB:CC:DD:EE:01", "action": "allow", "description": "printer"},
                    ],
                },
                "GigabitEthernet0/2": {
                    "name": "GigabitEthernet0/2",
                    "policy": "disabled",
                    "entries": [],
                },
            }
        """
        raise NotImplementedError

    def get_dot1x_config(self) -> Dict[str, Dot1XPortDict]:
        """
        Returns the 802.1X / NAC configuration per switch port.

        Keys are interface names.  Each value contains:

        * enabled (bool) - whether 802.1X is active on this port
        * port_control (string) - authentication mode:

          * ``"auto"`` – port authenticates normally
          * ``"force-authorized"`` – port always passes traffic (bypass)
          * ``"force-unauthorized"`` – port always blocks traffic

        * host_mode (string) - how many identities are authenticated per port:

          * ``"single-host"`` – one device, then port is locked
          * ``"multi-host"`` – first auth unlocks port for all devices
          * ``"multi-domain"`` – one data + one voice device (IP phone scenario)
          * ``"multi-auth"`` – each device authenticates individually

        * auth_server (dict) - RADIUS authentication server (host, port, timeout, retries)
        * acct_server (dict or None) - RADIUS accounting server, ``None`` if unused
        * reauthentication (bool) - whether periodic re-authentication is enabled
        * reauth_interval (int) - re-authentication interval in seconds (0 = disabled)
        * guest_vlan (int) - VLAN ID for unauthenticated clients (0 = disabled)
        * auth_fail_vlan (int) - VLAN ID for clients that fail authentication (0 = disabled)

        Note: RADIUS shared secrets are intentionally omitted.

        Example::

            {
                "GigabitEthernet0/1": {
                    "enabled": True,
                    "port_control": "auto",
                    "host_mode": "multi-domain",
                    "auth_server": {
                        "host": "radius.corp.example",
                        "port": 1812,
                        "timeout": 5,
                        "retries": 3,
                    },
                    "acct_server": None,
                    "reauthentication": True,
                    "reauth_interval": 3600,
                    "guest_vlan": 99,
                    "auth_fail_vlan": 999,
                },
            }
        """
        raise NotImplementedError

    def get_poe_status(self) -> PoESummaryDict:
        """
        Returns the PoE status of the switch as a whole and per port.

        The returned dictionary contains:

        * total_power_budget (float) - total PoE power available in watts
        * total_power_draw (float) - total PoE power currently consumed in watts
        * ports (dict) - per-interface PoE state, keyed by interface name:

          * enabled (bool) - whether PoE is configured on this port
          * status (string) - operational state:

            * ``"delivering"`` – power is being delivered to a PD
            * ``"searching"``  – port is looking for a powered device
            * ``"fault"``      – an error condition was detected
            * ``"disabled"``   – PoE is administratively off
            * ``"denied"``     – PD detected but power budget exceeded

          * poe_class (string) - IEEE 802.3 class: ``"Class 0"`` … ``"Class 8"``
            (``"unknown"`` if not yet negotiated)
          * power_draw (float) - current power consumption in watts
          * power_budget (float) - per-port power limit in watts
          * voltage (float) - measured port voltage in volts
          * current (float) - measured port current in milliamps

        Example::

            {
                "total_power_budget": 740.0,
                "total_power_draw": 43.2,
                "ports": {
                    "GigabitEthernet0/1": {
                        "enabled": True,
                        "status": "delivering",
                        "poe_class": "Class 3",
                        "power_draw": 12.4,
                        "power_budget": 30.0,
                        "voltage": 53.5,
                        "current": 231.0,
                    },
                    "GigabitEthernet0/2": {
                        "enabled": True,
                        "status": "searching",
                        "poe_class": "unknown",
                        "power_draw": 0.0,
                        "power_budget": 30.0,
                        "voltage": 0.0,
                        "current": 0.0,
                    },
                    "GigabitEthernet0/3": {
                        "enabled": False,
                        "status": "disabled",
                        "poe_class": "unknown",
                        "power_draw": 0.0,
                        "power_budget": 0.0,
                        "voltage": 0.0,
                        "current": 0.0,
                    },
                },
            }
        """
        raise NotImplementedError

    def set_poe_enabled(self, interface: str, enabled: bool) -> None:
        """
        Administratively enables or disables PoE on a single port.

        :param interface: Interface name (e.g. ``"GigabitEthernet0/1"``).
        :param enabled: ``True`` to enable PoE, ``False`` to disable it.
        :raises NotImplementedError: If the driver does not support PoE control.
        :raises ValueError: If the interface does not exist or does not support PoE.

        Example::

            driver.set_poe_enabled("GigabitEthernet0/1", False)  # cut power
            driver.set_poe_enabled("GigabitEthernet0/1", True)   # restore
        """
        raise NotImplementedError

    def power_cycle_port(self, interface: str, delay: int = 5) -> None:
        """
        Power-cycles the PoE port: cuts power, waits ``delay`` seconds, then
        restores power.  Useful for rebooting a hung IP camera, AP, or IP phone
        without physical access.

        The method blocks until the full cycle (off → wait → on) is complete.
        After it returns the port is back in the delivering/searching state.

        :param interface: Interface name (e.g. ``"GigabitEthernet0/1"``).
        :param delay: Seconds to keep the port powered off (default: 5).
        :raises NotImplementedError: If the driver does not support PoE control.
        :raises ValueError: If the interface does not exist, does not support PoE,
            or PoE is administratively disabled on the port.

        Example::

            driver.power_cycle_port("GigabitEthernet0/1")        # 5 s off
            driver.power_cycle_port("GigabitEthernet0/1", delay=15)  # 15 s off
        """
        raise NotImplementedError
