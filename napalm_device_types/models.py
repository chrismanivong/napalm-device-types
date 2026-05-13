"""
TypedDicts for NAPALM device-type-specific return values.

These supplement the types defined in napalm.base.models and are used by the
abstract device-type driver classes in this package.
"""

from typing import Dict, List, Optional
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# Common  (shared across device types)
# ---------------------------------------------------------------------------


class RadiusServerDict(TypedDict):
    host: str
    port: int
    timeout: int
    retries: int


class MACACLEntryDict(TypedDict):
    mac: str
    action: str
    description: str


class MACACLDict(TypedDict):
    """MAC access-control list for a single binding point.

    ``name`` is the SSID name on an access point, or the interface name on a
    switch.
    """

    name: str
    policy: str
    entries: List[MACACLEntryDict]


class PackageDict(TypedDict):
    """A software package / plugin installed on the device."""

    name: str
    version: str
    installed: bool
    description: str
    size: int
    source: str


# ---------------------------------------------------------------------------
# Access Point
# ---------------------------------------------------------------------------


class WirelessClientDict(TypedDict):
    mac: str
    ssid: str
    radio: str
    signal: int
    noise: int
    tx_rate: float
    rx_rate: float
    uptime: int


class SSIDDict(TypedDict):
    enabled: bool
    radio: str
    bssid: str
    encryption: str
    hidden: bool
    clients: int


class RadioStatusDict(TypedDict):
    enabled: bool
    band: str
    channel: int
    channel_width: int
    tx_power: int
    frequency: float


class WirelessConfigDict(TypedDict):
    country_code: str
    regulatory_domain: str
    beacon_interval: int
    dtim_period: int
    rts_threshold: int
    fragmentation_threshold: int
    short_preamble: bool
    wmm_enabled: bool


class FastTransitionConfigDict(TypedDict):
    enabled: bool
    ssid: str
    mobility_domain: str
    reassociation_deadline: int
    r0_key_lifetime: int
    r1_key_holder: str
    pmk_r1_push: bool
    over_ds: bool


class MeshPeerDict(TypedDict):
    mac: str
    radio: str
    signal: int
    tx_rate: float
    rx_rate: float
    uptime: int
    hop_count: int


class MeshConfigDict(TypedDict):
    enabled: bool
    radio: str
    mesh_id: str
    path_metric: str
    gate_announcements: bool
    is_gate: bool
    encryption: str


class SSIDBridgeDict(TypedDict):
    ssid: str
    bridge: str
    vlan_id: int
    tagged: bool
    client_isolation: bool


class Dot1XConfigDict(TypedDict):
    """802.1X / WPA-Enterprise config for an access-point SSID."""

    enabled: bool
    ssid: str
    auth_server: RadiusServerDict
    acct_server: Optional[RadiusServerDict]
    reauth_interval: int
    pmksa_caching: bool


# ---------------------------------------------------------------------------
# Switch
# ---------------------------------------------------------------------------


class InterfaceConfigDict(TypedDict, total=False):
    """Settable configuration for a single switch interface.

    All fields are optional – only the fields present in the dict are applied;
    omitted fields are left unchanged on the device.

    * description (str) – human-readable port label
    * enabled (bool) – administrative state (``True`` = no shutdown)
    * speed (int) – link speed in Mbps; ``0`` = auto-negotiate
    * duplex (str) – ``"full"``, ``"half"``, or ``"auto"``
    * mtu (int) – maximum transmission unit in bytes
    * mode (str) – port mode: ``"access"``, ``"trunk"``, or ``"routed"``
    * access_vlan (int) – untagged VLAN ID; effective when *mode* is ``"access"``
    * voice_vlan (int) – voice VLAN ID (``0`` = disabled)
    * trunk_vlans (list of int) – tagged VLAN IDs allowed on trunk;
      empty list means *all* VLANs; effective when *mode* is ``"trunk"``
    * native_vlan (int) – native (untagged) VLAN on a trunk port
    """

    description: str
    enabled: bool
    speed: int
    duplex: str
    mtu: int
    mode: str
    access_vlan: int
    voice_vlan: int
    trunk_vlans: List[int]
    native_vlan: int


class VlanConfigDict(TypedDict, total=False):
    """Settable configuration for a single VLAN.

    All fields are optional – only those present are applied.

    * name (str) – human-readable VLAN name
    * active (bool) – whether the VLAN is active (``True``) or suspended (``False``)
    * interfaces (list of str) – access-port interface names that should be
      assigned to this VLAN (replaces the current membership)
    """

    name: str
    active: bool
    interfaces: List[str]


class STPInterfaceDict(TypedDict):
    role: str
    state: str
    cost: int
    port_priority: int


class SpanningTreeDict(TypedDict):
    mode: str
    root_bridge: bool
    root_id: str
    root_priority: int
    bridge_id: str
    bridge_priority: int
    interfaces: Dict[str, STPInterfaceDict]


class PortChannelDict(TypedDict):
    members: List[str]
    protocol: str
    min_links: int
    is_up: bool


class Dot1XPortDict(TypedDict):
    """802.1X / NAC configuration for a single switch port."""

    enabled: bool
    port_control: str
    host_mode: str
    auth_server: RadiusServerDict
    acct_server: Optional[RadiusServerDict]
    reauthentication: bool
    reauth_interval: int
    guest_vlan: int
    auth_fail_vlan: int


class PoEPortDict(TypedDict):
    enabled: bool
    status: str
    poe_class: str
    power_draw: float
    power_budget: float
    voltage: float
    current: float


class PoESummaryDict(TypedDict):
    total_power_budget: float
    total_power_draw: float
    ports: Dict[str, PoEPortDict]


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------


class NATTranslationDict(TypedDict):
    protocol: str
    inside_local: str
    inside_global: str
    outside_local: str
    outside_global: str
    age: float


class SecurityZoneDict(TypedDict):
    interfaces: List[str]
    policy: str
    description: str


class SessionDict(TypedDict):
    protocol: str
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    state: str
    age: float


class VPNTunnelDict(TypedDict):
    type: str
    local_endpoint: str
    remote_endpoint: str
    is_up: bool
    uptime: int
    bytes_in: int
    bytes_out: int


# ---------------------------------------------------------------------------
# Hypervisor
# ---------------------------------------------------------------------------


class VMDiskDict(TypedDict):
    device: str
    storage: str
    size: int
    format: str
    bootable: bool


class VMNICDict(TypedDict):
    device: str
    mac: str
    model: str
    bridge: str
    vlan_id: int


class VMDict(TypedDict):
    name: str
    vmid: int
    status: str
    vcpus: int
    memory: int
    cpu_usage: float
    memory_usage: int
    uptime: int
    node: str


class VMConfigDict(TypedDict):
    name: str
    vmid: int
    vcpus: int
    memory: int
    os_type: str
    boot_order: List[str]
    disks: List[VMDiskDict]
    nics: List[VMNICDict]
    description: str
    tags: List[str]


class StorageVolumeDict(TypedDict):
    name: str
    type: str
    total: int
    used: int
    available: int
    enabled: bool
    shared: bool


class VirtualNetworkDict(TypedDict):
    name: str
    type: str
    bridge: str
    vlan_id: int
    autostart: bool
    active: bool


class SnapshotDict(TypedDict):
    name: str
    vm: str
    created: float
    description: str
    has_memory: bool
    parent: str


# ---------------------------------------------------------------------------
# Storage / NAS
# ---------------------------------------------------------------------------


class PhysicalDiskDict(TypedDict):
    """A physical drive installed in the storage device."""

    slot: str
    model: str
    serial: str
    vendor: str
    type: str          # "hdd", "ssd", "nvme"
    size: int          # bytes
    rpm: int           # 0 for SSD/NVMe
    temperature: int   # Celsius; -1 if unavailable
    health: str        # "healthy", "warning", "failed", "unknown"
    pool: str          # name of the containing pool; empty string if spare/unassigned


class DiskPoolDict(TypedDict):
    """A RAID array, ZFS pool, or volume group."""

    name: str
    type: str          # "zfs", "lvm", "md", "hardware-raid", "btrfs"
    level: str         # "stripe", "mirror", "raidz1", "raidz2", "raidz3",
                       # "raid0" … "raid60", "single", etc.
    status: str        # "online", "degraded", "faulted", "offline", "unknown"
    total: int         # bytes
    used: int          # bytes
    available: int     # bytes
    disks: List[str]   # slot identifiers of member disks
    auto_expand: bool
    dedup: bool
    compression: str   # "off", "lz4", "gzip", "zstd", etc.


class LogicalVolumeDict(TypedDict):
    """A logical volume, ZFS dataset, or LUN exposed to clients."""

    name: str
    pool: str
    type: str          # "filesystem", "volume" (block device / LUN), "zvol"
    total: int         # bytes
    used: int          # bytes
    available: int     # bytes
    mountpoint: str    # empty string for block volumes
    compression: str   # "off", "lz4", etc.
    dedup: bool
    readonly: bool
    snapshots: int     # number of snapshots currently held


class NASShareDict(TypedDict):
    """A network share or iSCSI target exported by the storage device."""

    name: str
    protocol: str      # "nfs", "smb", "afp", "ftp", "sftp", "iscsi", "webdav"
    path: str          # local filesystem path or iSCSI target IQN
    volume: str        # logical volume or dataset this share is backed by
    enabled: bool
    readonly: bool
    description: str
    clients: List[str] # IP/subnet allow-list; empty list = all hosts allowed


class VolumeSnapshotDict(TypedDict):
    """A point-in-time snapshot of a logical volume or dataset."""

    name: str
    volume: str        # parent volume / dataset
    created: float     # Unix epoch
    size: int          # bytes of unique data referenced by this snapshot
    description: str
    clones: List[str]  # volumes cloned from this snapshot


class StorageQuotaDict(TypedDict):
    """A filesystem quota applied to a user, group, or dataset."""

    target: str        # username, group name, or dataset path
    target_type: str   # "user", "group", "dataset"
    volume: str        # volume / dataset the quota applies to
    used: int          # bytes currently used
    quota: int         # hard limit in bytes; 0 = no limit
    ref_quota: int     # referenced-data limit in bytes; 0 = no limit


class StorageServiceDict(TypedDict):
    """Status of a file-sharing or access service running on the device."""

    name: str          # "nfs", "smb", "ftp", "ssh", "iscsi", "webdav", etc.
    enabled: bool      # administratively enabled
    running: bool      # currently active / listening
    port: int          # primary listening port; 0 if N/A
    version: str       # protocol version string (e.g. "4.1" for NFSv4.1)


class ReplicationJobDict(TypedDict):
    """A scheduled replication or sync task."""

    name: str
    source: str        # source path / dataset
    target: str        # destination path / dataset (may be remote: host:path)
    direction: str     # "push" or "pull"
    schedule: str      # cron expression or human label ("daily", "hourly")
    enabled: bool
    last_run: float    # Unix epoch; 0.0 if never run
    last_status: str   # "success", "failed", "running", "pending"
    bytes_sent: int    # bytes transferred in the last run
