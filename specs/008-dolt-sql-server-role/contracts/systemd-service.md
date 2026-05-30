# Contract: systemd Service (`dolt-sql-server.service`)

Rendered from `templates/dolt-sql-server.service.j2`. Defines the boot and
restart behaviour required by FR-002, FR-003, SC-002, SC-005.

## Unit contract

```ini
[Unit]
Description=Dolt SQL Server
After=network.target

[Service]
Type=simple
User={{ dolt_service_user }}
ExecStart={{ dolt_install_path }} sql-server --config={{ dolt_config_path }}
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

## Behavioural guarantees

| Directive | Requirement satisfied |
| --- | --- |
| `WantedBy=multi-user.target` + unit `enabled` | Starts automatically on every boot, including first boot after provisioning (FR-002, SC-002). |
| `Restart=always`, `RestartSec=2` | Service restarts after an unexpected stop/crash (FR-003, SC-005). |
| `User={{ dolt_service_user }}` | Runs unprivileged (least privilege). |
| `ExecStart ... --config` | Loopback-only listener via the config file (FR-007). |

## Lifecycle management (Ansible)

- `ansible.builtin.systemd_service`: `daemon_reload: true` (on change),
  `enabled: true`, `state: started`.
- Applied only where `ansible_facts['service_mgr'] == 'systemd'` (D6). In a
  non-systemd container the unit file is still rendered for inspection, but
  enable/start are skipped (explicit environment guard).
- Config or unit changes notify a handler: `daemon_reload` → restart. An
  unchanged re-run performs no restart (FR-005, SC-003).

## Validation

- **Molecule (container)**: assert unit file exists and contains
  `Restart=always` and `WantedBy=multi-user.target`. Enable/start not exercised
  (no PID1 systemd).
- **VM (Vagrant/cloud, Principle III)**: `systemctl is-enabled` →
  `enabled`; `systemctl is-active` → `active`; reboot → service active before
  login; `systemctl kill` → service auto-restarts. Procedure in
  `quickstart.md`.
