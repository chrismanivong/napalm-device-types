"""
napalm-device-types
~~~~~~~~~~~~~~~~~~~

Abstract device-type base classes for NAPALM drivers.

Instead of inheriting directly from ``napalm.base.NetworkDriver``, a driver
can inherit from one of the device-type classes defined here to gain
type-specific abstract methods and a clearer contract::

    from napalm_device_types import AccessPointDriver

    class OpenWrtDriver(AccessPointDriver):
        ...

Available base classes:

* :class:`~napalm_device_types.access_point.AccessPointDriver`
* :class:`~napalm_device_types.switch.SwitchDriver`
* :class:`~napalm_device_types.firewall.FirewallDriver`
* :class:`~napalm_device_types.hypervisor.HypervisorDriver`
* :class:`~napalm_device_types.storage.StorageDriver`
"""

from napalm_device_types.access_point import AccessPointDriver
from napalm_device_types.firewall import FirewallDriver
from napalm_device_types.hypervisor import HypervisorDriver
from napalm_device_types.storage import StorageDriver
from napalm_device_types.switch import SwitchDriver

__all__ = [
    "AccessPointDriver",
    "FirewallDriver",
    "HypervisorDriver",
    "StorageDriver",
    "SwitchDriver",
]
