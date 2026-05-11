# napalm-device-types

Abstract intermediate device-type base classes for [NAPALM](https://napalm.readthedocs.io/) drivers.

Instead of inheriting directly from `napalm.base.NetworkDriver`, a driver can inherit from one of the device-type classes here to gain a richer, type-specific contract:

```python
# without napalm-device-types
class OpenWrtDriver(NetworkDriver):
    ...

# with napalm-device-types
from napalm_device_types import AccessPointDriver

class OpenWrtDriver(AccessPointDriver):
    ...
```

## Why?

NAPALM's `NetworkDriver` defines a common interface for all network devices. In practice, devices fall into distinct categories with very different capabilities. A switch exposes spanning-tree and PoE data; a firewall exposes NAT tables and VPN tunnels; a NAS exposes disk pools and shares. Writing these methods directly in a concrete driver mixes concerns and makes drivers harder to discover and compare.

`napalm-device-types` sits in between: it adds one well-typed layer of abstract methods per device category, so every driver for the same category exposes the same interface.

## Installation

```bash
pip install napalm-device-types
```

Requires Python ≥ 3.9 and NAPALM ≥ 4.0.

## Available base classes

| Class | Target devices | Example implementations |
|---|---|---|
| `AccessPointDriver` | Wireless access points | OpenWrt, Ubiquiti UniFi, Cisco Meraki AP |
| `SwitchDriver` | Ethernet switches | Cisco IOS, Arista EOS, Juniper EX |
| `FirewallDriver` | Firewalls & UTM appliances | pfSense, Fortinet FortiOS, Cisco ASA |
| `HypervisorDriver` | Hypervisors & virtualisation platforms | Proxmox VE, VMware ESXi, KVM/libvirt |
| `StorageDriver` | Storage appliances & NAS/SAN | TrueNAS, Synology DSM, QNAP QTS |

## Usage

### Access Point

```python
from napalm_device_types import AccessPointDriver

class OpenWrtDriver(AccessPointDriver):

    def get_wireless_clients(self):
        # return List[WirelessClientDict]
        ...

    def get_ssids(self):
        # return Dict[str, SSIDDict]
        ...
```

### Switch

```python
from napalm_device_types import SwitchDriver

class CiscoIOSDriver(SwitchDriver):

    def get_spanning_tree(self):
        # return Dict[str, SpanningTreeDict]
        ...

    def get_poe_status(self):
        # return PoESummaryDict
        ...
```

### Firewall

```python
from napalm_device_types import FirewallDriver

class PfSenseDriver(FirewallDriver):

    def get_nat_translations(self):
        # return List[NATTranslationDict]
        ...

    def get_vpn_tunnels(self):
        # return Dict[str, VPNTunnelDict]
        ...
```

### Hypervisor

```python
from napalm_device_types import HypervisorDriver

class ProxmoxDriver(HypervisorDriver):

    def get_vms(self):
        # return List[VMDict]
        ...

    def snapshot_create(self, name, snapshot, description="", include_memory=False):
        ...
```

### Storage / NAS

```python
from napalm_device_types import StorageDriver

class TrueNASDriver(StorageDriver):

    def get_disks(self):
        # return List[PhysicalDiskDict]
        ...

    def get_shares(self):
        # return Dict[str, NASShareDict]
        ...
```

## Return types

All return types are `TypedDict` classes defined in `napalm_device_types.models`. Import them directly for type annotations in your driver:

```python
from napalm_device_types.models import (
    PhysicalDiskDict,
    DiskPoolDict,
    NASShareDict,
    VolumeSnapshotDict,
)
```

## Development

```bash
git clone https://github.com/chrismanivong/napalm-device-types.git
cd napalm-device-types
pip install -e ".[dev]"
```

Run type-checking:

```bash
mypy napalm_device_types
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/router-driver`)
3. Implement your changes
4. Open a Pull Request

## License

Apache-2.0 – see [LICENSE](LICENSE) for details.
