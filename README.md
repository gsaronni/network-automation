# Network Automation Tools

Production automation tools for enterprise network operations. Built to solve real operational challenges in multi-vendor environments.

[![Python 3.7+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Bash](https://img.shields.io/badge/bash-5.0+-green.svg)](https://www.gnu.org/software/bash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Projects

## At a Glance

**Two production automation tools solving real operational problems:**

| Tool | Problem Solved | Impact | Status |
|------|----------------|--------|--------|
| **F5 BigIP Automation** | Manual node management during patching (50 min/month) | **98% time reduction** (50 min → <1 min) | Production-stable v1.6 |
| **Network Backup Orchestrator** | Manual multi-vendor config backups | Automated backup for 6 device types, zero manual intervention | Production-hardened v5.0 |

**Technology Stack:** Bash, Python 3.7+, Netmiko, Paramiko, F5 iControl, PyQt5  
**Environment:** Enterprise multi-vendor (Cisco, F5, Linux)

### 🔧 F5 BigIP Patching Automation

**Problem:** Monthly patching required manually disabling/enabling 30+ F5 LTM nodes across three partitions (BE-PRO, BE-OMT, FE-DMZ). Process took 50+ minutes, high risk of human error affecting production traffic.

**Solution:** Interactive bash automation using F5 tmsh API for bulk node state management. Handles three distinct patching scenarios with built-in validation.

**Impact:**
- ⏱️ **98% time reduction**: 50 minutes → <1 minute per maintenance window
- 🎯 **Zero errors**: Eliminated manual mistakes in 18+ months production use
- 📊 **Annual savings**: ~20 engineer-hours

**Technical Details:**
- **Technology**: Bash 5.0+, F5 tmsh CLI, iControl REST API
- **Architecture**: Interactive CLI → Partition selection → Bulk node operations → Validation
- **Production Status**: v1.6 (stable, actively maintained)

📖 [View detailed documentation](BIG-IP-F5_LTM_nodes.md)
---

### 🌐 Network Backup Orchestrator

**Problem:** Manual configuration backups across 6 different device types (Cisco NX-OS, IOS, ASA multi-context, ISE, Linux) with inconsistent processes and no centralized storage.

**Solution:** Python orchestration tool with unified interface for multi-vendor backups, pre-flight validation, and automated SFTP archival.

**Impact:**
- 🔄 **Automated daily backups**: Zero manual intervention
- 🛡️ **Pre-flight validation**: Catches credential/connectivity issues before backup runs
- 📦 **Multi-context ASA support**: Handles complex firewall configurations (most tools fail here)

**Technical Details:**
- **Technology**: Python 3.7+, Netmiko, Paramiko, PyQt5
- **Supported Platforms**: 
  - Cisco: NX-OS, IOS, ASA (including multi-context), ISE
  - Linux: SSH-based config retrieval
- **Architecture**: GUI credential management → Device discovery → Sequential backup execution → SFTP upload → Local archival

**Evolution Timeline:**
- **v1.0** (2020): Basic single-vendor backup
- **v2.0** (2021): Added multi-vendor support (Nexus, IOS)
- **v3.0** (2021): ASA multi-context handling (solved complex partition logic)
- **v4.0** (2022): Pre-flight validation system
- **v5.0** (2023): SFTP automation + error recovery

*Evolved through 3 years of production use, handling real operational failures and edge cases.*

📖 [View detailed documentation](network-backup.md)
---

## Quick Start

### Prerequisites
- Python 3.7+
- Network access to target devices
- SSH credentials for devices

### Installation

**Clone repository:**
```bash
git clone https://github.com/gsaronni/network-automation-toolkit.git
cd network-automation-toolkit
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### F5 Patching Automation
```bash
chmod +x f5-patching-automation.sh
./f5-patching-automation.sh
```

**Interactive prompts guide you through:**
1. Partition selection (BE-PRO/BE-OMT/FE-DMZ)
2. Patching scenario (Windows/Linux/Firewall)
3. Automated node disable → patching window → re-enable

### Network Backup Orchestrator

⚠️ **Note:** Script uses Windows-specific paths. Linux/Mac users need to modify `path` variable in script.
```bash
python network-backup-orchestrator.py
```

**First-run prompts:**
- Your network username (auto-detected from `$USERNAME`)
- Device passwords (hidden input via `getpass`)
- Backup server credentials

**Output locations:**
- Fresh backups: `~/Documents/backupFastDelivery/todayBackup/`
- Archives: `~/Documents/backupFastDelivery/backupArchive/{date}/`
- Logs: `~/Documents/backupFastDelivery/logs/`

**Supported devices (auto-detected):**
- Cisco Nexus switches (NX-OS)
- Cisco ASR routers (IOS)
- Cisco ISE appliances
- Cisco ASA firewalls (multi-context)
- Linux servers via SSH

## Philosophy

These tools embody practical network automation:
- **Solve real problems**: Built for actual operational pain points
- **Production-ready**: Battle-tested in enterprise environments
- **Maintainable**: Clear code, comprehensive documentation
- **Progressive**: Simple solutions first, complexity only when needed

## Known Limitations & Future Roadmap

### Current Constraints
- **F5 Script**: 
  - Bash-based (not idempotent, no state tracking)
  - No automated testing (relies on manual validation)
  - Single-BigIP focus (no HA pair handling)
  
- **Python Backup Tool**:
  - PyQt5 GUI requires display (not server-friendly)
  - No containerization (environment-dependent)
  - Credentials in GUI storage (not vault-integrated)

### Planned Improvements
- [ ] **F5 Automation**: Migrate to Ansible playbook using `f5networks.f5_modules` collection
- [ ] **Python Tool**: Containerize with Docker for reproducible environments
- [ ] **Testing**: Add pytest suite with mocked device responses
- [ ] **CI/CD**: GitHub Actions workflow for automated testing
- [ ] **Secrets Management**: Integrate with HashiCorp Vault / Ansible Vault

*These tools reflect practical solutions built for immediate operational needs. Modernization efforts focus on current best practices while maintaining production stability.*

## Author

**Gabriele Saronni**  
Network Engineer & Automation Developer

[LinkedIn](https://linkedin.com/in/gabriele-s-54514173) | [GitHub](https://github.com/gsaronni)

---

*Tools developed from real operational experience in enterprise telecommunications infrastructure.*
