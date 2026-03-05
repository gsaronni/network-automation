# Ansible Backup - Learning Project

Converting the Python backup orchestrator to Ansible playbooks as practice.

## Why

- Learn Ansible syntax and network modules
- Practice infrastructure-as-code patterns
- Understand inventory management vs hardcoded IPs

## Install
```bash
pip install ansible
ansible-galaxy collection install cisco.ios
```

## Run
```bash
ansible-playbook -i inventory.ini backup-configs.yml --ask-pass
```

## Status

Basic Nexus/ASR backup works. ASA multi-context and SFTP upload not implemented yet.

## Comparison to Python Script

**Python:** 400 lines, hardcoded IPs, custom error handling, PyQt5 GUI  
**Ansible:** ~50 lines, inventory file, built-in modules, CLI prompts

Both approaches work. This is just demonstrating Ansible knowledge for portfolio.
