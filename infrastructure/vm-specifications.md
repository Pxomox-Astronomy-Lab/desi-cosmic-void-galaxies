<!--
---
title: "VM Specifications"
description: "Detailed virtual machine configurations and resource allocation for DESI cosmic void analysis infrastructure, including database and analysis platform specifications"
author: "VintageDon"
ai_contributor: "Anthropic Claude 4 Sonnet (claude-4-sonnet-20250514)"
date: "2025-07-01"
version: "1.0"
status: "Published"
tags:
- type: infrastructure
- domain: virtualization
- domain: resource-allocation
- tech: proxmox
- tech: postgresql-16
- phase: project-setup
related_documents:
- "[Infrastructure Overview](README.md)"
- "[Database Infrastructure](database/README.md)"
- "[Deployment Infrastructure](deployment/README.md)"
- "[Project Architecture](../docs/project-architecture.md)"
scientific_context:
  objective: "Environmental quenching analysis"
  dataset: "DESI DR1 BGS"
  methods: ["infrastructure-specification", "resource-allocation"]
---
-->

# 💻 **VM Specifications**

This document provides detailed virtual machine configurations and resource allocation for DESI cosmic void analysis infrastructure, including comprehensive specifications for database servers, analysis platforms, and backup infrastructure supporting 27.6GB DESI DR1 data processing and environmental quenching research.

# 🎯 **1. Introduction**

This section establishes the foundational context for VM specifications within the DESI cosmic void analysis project, defining the systematic approach to virtual infrastructure that enables reliable scientific computing and efficient resource utilization.

## **1.1 Purpose**

This subsection explains how VM specifications enable systematic resource allocation and infrastructure planning while supporting efficient DESI data processing and environmental analysis workflows for cosmic void research.

The VM specifications function as the systematic foundation for DESI cosmic void analysis infrastructure, transforming hardware resources into optimized, dedicated, and manageable virtual computing environments supporting scientific research workflows. The specifications provide detailed resource allocation for PostgreSQL database operations, Python scientific computing, and comprehensive backup infrastructure, enabling efficient processing of 27.6GB DESI DR1 data and systematic environmental classification workflows. The infrastructure supports systematic scientific analysis through appropriate resource allocation, performance optimization, and operational reliability essential for environmental quenching research validation and publication preparation.

## **1.2 Scope**

This subsection defines the boundaries of VM specification coverage within the DESI cosmic void analysis project.

| **In Scope** | **Out of Scope** |
|--------------|------------------|
| Virtual machine resource allocation and configuration specifications | Physical hardware procurement and data center infrastructure |
| Database server and analysis platform VM specifications | Network infrastructure and switch configuration details |
| Backup infrastructure VM requirements and storage allocation | Application software installation and configuration procedures |
| Performance requirements and resource optimization guidelines | Detailed monitoring configuration and alerting setup |
| VM deployment planning and migration procedures | Security configuration and access control implementation |

## **1.3 Target Audience**

This subsection identifies stakeholders who interact with VM specifications and the technical background required for effective infrastructure planning and resource management.

**Primary Audience:** Infrastructure engineers, virtualization specialists, and system administrators responsible for VM deployment and resource management. **Secondary Audience:** Database administrators, platform engineers, and scientific researchers who need to understand computational resources and performance capabilities. **Required Background:** Understanding of virtualization technologies, resource allocation concepts, and infrastructure planning principles.

## **1.4 Overview**

This subsection provides context about VM specification organization and its relationship to the broader DESI cosmic void analysis project infrastructure and scientific computing requirements.

The VM specifications establish systematic infrastructure foundation, transforming hardware capabilities into optimized, dedicated, and manageable virtual environments that enable reliable scientific computing, efficient data processing, and systematic environmental analysis through comprehensive resource allocation and performance optimization frameworks.

# 🔗 **2. Dependencies & Relationships**

This section maps how VM specifications integrate with infrastructure components and establish resource relationships that enable systematic scientific computing and environmental research workflows.

## **2.1 Related Services**

This subsection identifies infrastructure components that depend on or interact with VM specifications and resource allocation.

| **Service** | **Relationship Type** | **Integration Points** | **Documentation** |
|-------------|----------------------|------------------------|-------------------|
| **Database Infrastructure** | **Hosts** | PostgreSQL deployment, storage allocation, performance optimization | [Database Infrastructure](database/README.md) |
| **Deployment Procedures** | **Guides** | VM provisioning, configuration management, automation procedures | [Deployment Infrastructure](deployment/README.md) |
| **Operations Management** | **Monitors** | Resource utilization, performance tracking, capacity planning | [Operations Infrastructure](operations/README.md) |
| **Project Architecture** | **Implements** | System design requirements, component integration, resource planning | [Project Architecture](../docs/project-architecture.md) |

## **2.2 Policy Implementation**

This subsection connects VM specifications to infrastructure governance and resource management requirements.

VM specifications implementation directly supports several critical infrastructure objectives:

- **Resource Management Policy** - Systematic resource allocation enabling efficient utilization and performance optimization
- **Capacity Planning Policy** - Strategic resource planning supporting scalable scientific computing and analysis workflows
- **Performance Policy** - Optimized resource allocation ensuring adequate performance for DESI data processing requirements
- **Security Architecture Policy** - Appropriate resource isolation and security boundary implementation aligned with compliance frameworks
- **Operational Excellence Policy** - Systematic resource management supporting reliable operations and maintenance procedures

**Compliance Framework**: VM infrastructure aligns with CIS Controls v8 and NIST frameworks through systematic security configuration and resource management. Ubuntu 24.04 servers are baselined to CIS v8 Level 2. Note: We are not security professionals and are working towards full compliance validation with established frameworks.

## **2.3 Responsibility Matrix**

This subsection establishes clear accountability for VM specification activities across infrastructure roles.

| **Activity** | **Infrastructure Engineers** | **Virtualization Specialists** | **System Administrators** | **Database Administrators** |
|--------------|------------------------------|--------------------------------|---------------------------|----------------------------|
| **Resource Planning** | **A** | **R** | **C** | **C** |
| **VM Deployment** | **R** | **A** | **C** | **I** |
| **Performance Optimization** | **R** | **C** | **A** | **R** |
| **Capacity Management** | **A** | **R** | **R** | **C** |
| **Resource Monitoring** | **C** | **C** | **A** | **R** |

*R: Responsible, A: Accountable, C: Consulted, I: Informed*

# ⚙️ **3. Technical Implementation**

This section provides comprehensive specifications for virtual machine configurations, resource allocation, and performance requirements that support DESI cosmic void analysis and environmental research workflows.

## **3.1 Architecture & Design**

This subsection explains the VM architecture and design decisions that enable efficient resource utilization and optimal performance for DESI data processing and scientific analysis.

The VM architecture employs dedicated virtual machines with specialized resource allocation for database operations and scientific computing workloads. The design features optimized resource allocation based on workload characteristics, systematic storage allocation supporting high-performance data access, and comprehensive backup infrastructure ensuring data protection and operational continuity.

## **3.2 Structure and Organization**

This subsection describes the VM organization and detailed specifications that support DESI cosmic void analysis infrastructure requirements.

### **Database Server: proj-pg01 (VM ID: 2002)**

**Primary Function:** PostgreSQL 16 database server optimized for astronomical data processing

| **Specification** | **Allocation** | **Justification** |
|-------------------|----------------|-------------------|
| **vCPU** | **8 cores (2 sockets, 4 cores each)** | Optimal for PostgreSQL concurrent operations and spatial query processing |
| **Memory** | **48GB RAM (8GB pre-allocated)** | Sufficient for 12GB shared_buffers + 36GB effective_cache_size + OS overhead |
| **Boot Storage** | **32GB** | Ubuntu 24.04 system installation with adequate space for updates |
| **Data Storage** | **250GB NVMe** | High-performance storage for PostgreSQL data directory and 27.6GB DESI catalogs |
| **Network** | **1x 10G interface (VLAN 20)** | High-bandwidth connectivity for data ingestion and analysis queries |

**Resource Allocation Details:**

- **IP Address:** 10.25.20.8
- **Hostname:** proj-pg01.radioastronomy.io
- **Operating System:** Ubuntu 24.04 LTS (CIS v8 Level 2 baseline)
- **PostgreSQL Configuration:** Optimized for astronomical data with Q3C spatial indexing
- **Storage Path:** /mnt/data/pg01 (relocated for performance optimization)

**Performance Characteristics:**

- **Concurrent Connections:** Up to 200 (configured for cluster workers + analysts)
- **Query Performance:** Optimized for spatial queries and large table joins
- **Data Ingestion:** Bulk loading capability for 27.6GB FITS catalog processing
- **Backup Integration:** Daily automated backup to pbs01 with retention policies

### **Analysis Platform: proj-dp01 (VM ID: 2001)**

**Primary Function:** Python scientific computing platform for DESI data analysis

| **Specification** | **Allocation** | **Justification** |
|-------------------|----------------|-------------------|
| **vCPU** | **4 cores (2 sockets, 2 cores each)** | Adequate for Python scientific computing and statistical analysis workflows |
| **Memory** | **16GB RAM (2GB pre-allocated)** | Sufficient for pandas dataframes, statistical analysis, and visualization generation |
| **Boot Storage** | **32GB** | Ubuntu 24.04 system installation with development tools and libraries |
| **Data Storage** | **100GB NVMe** | Storage for analysis scripts, intermediate results, and publication outputs |
| **Network** | **1x 10G interface (VLAN 20)** | High-bandwidth connectivity for database queries and result transfer |

**Resource Allocation Details:**

- **IP Address:** 10.25.20.3
- **Hostname:** proj-dp01.radioastronomy.io
- **Operating System:** Ubuntu 24.04 LTS (CIS v8 Level 2 baseline)
- **Python Environment:** Scientific computing stack with astropy, pandas, scipy, matplotlib
- **Development Tools:** Jupyter notebooks, Git, development utilities

**Performance Characteristics:**

- **Analysis Workloads:** Statistical analysis, visualization generation, scientific computing
- **Database Connectivity:** Optimized SQLAlchemy connections to proj-pg01
- **Memory Management:** Efficient pandas operations for large dataset analysis
- **Output Generation:** Publication-quality plots and enhanced catalog production

### **Backup Infrastructure: pbs01**

**Primary Function:** Proxmox Backup Server for comprehensive data protection

| **Specification** | **Allocation** | **Justification** |
|-------------------|----------------|-------------------|
| **Hardware** | **Intel Twin Lake N150** | Dedicated mini PC for backup operations |
| **Memory** | **16GB DDR4** | Adequate for backup operations and deduplication processing |
| **Boot Storage** | **512GB PCIe 3.0 M.2 SSD** | System installation and backup software |
| **Backup Storage** | **4TB Samsung 990 Pro NVMe** | High-performance storage for backup data and deduplication |
| **Network** | **2.5GbE** | High-speed connectivity for backup data transfer |

**Backup Infrastructure Details:**

- **IP Address:** 10.16.207.218
- **Hostname:** pbs01.radioastronomy.io
- **Software:** Proxmox Backup Server with deduplication and compression
- **Backup Schedule:** Daily backups with 7 daily + 4 weekly + 1 monthly retention
- **Archive Integration:** Amazon S3 Glacier Infrequent Access for long-term storage

## **3.3 Integration and Procedures**

This subsection provides systematic overview of VM integration patterns and deployment procedures supporting scientific computing and environmental analysis workflows.

VM integration follows systematic approach: dedicated resource allocation optimized for specific workload characteristics, network configuration enabling high-bandwidth data access between components, systematic backup integration ensuring data protection, and comprehensive monitoring supporting resource utilization tracking and performance optimization. The implementation enables efficient scaling and resource management while maintaining performance and reliability requirements for scientific analysis workflows.

# 🛠️ **4. Management & Operations**

This section covers VM management approaches and operational procedures for maintaining infrastructure effectiveness and supporting ongoing scientific research requirements.

## **4.1 Lifecycle Management**

This subsection documents management approaches throughout the VM operational lifecycle and infrastructure evolution requirements.

VM lifecycle management encompasses deployment planning and resource allocation, systematic provisioning through Proxmox automation, performance monitoring and optimization procedures, capacity planning and scaling assessment, and systematic maintenance ensuring continued VM effectiveness and resource optimization throughout project lifecycle.

## **4.2 Monitoring & Quality Assurance**

This subsection defines monitoring strategies and quality approaches for VM performance and resource utilization validation.

VM monitoring includes resource utilization tracking across CPU, memory, storage, and network components, performance validation ensuring adequate capacity for scientific workloads, capacity planning assessment for future scaling requirements, and systematic quality assurance ensuring VM reliability and optimal performance for DESI analysis requirements.

## **4.3 Maintenance and Optimization**

This subsection outlines systematic maintenance and optimization approaches for VM evolution and performance enhancement.

VM maintenance encompasses systematic performance optimization, resource allocation adjustment based on utilization patterns, capacity planning and scaling procedures, security update management, and systematic improvement of VM configuration based on scientific computing requirements and performance optimization needs.

# 🔒 **5. Security & Compliance**

This section documents security controls and compliance alignment for VM infrastructure within the DESI cosmic void analysis project.

## **5.1 Security Controls**

This subsection documents specific security measures and verification methods for VM infrastructure and resource management.

VM security implementation includes systematic security configuration across all virtual machines, network isolation and access control implementation, resource-based security boundary enforcement, comprehensive audit logging for VM access and configuration changes, and systematic security monitoring aligned with CIS Controls v8 baseline requirements. Security controls ensure appropriate protection while enabling efficient scientific computing and research collaboration.

**Compliance Disclaimer**: We are not security professionals - this represents our baseline security implementation and we are working towards full compliance with established frameworks.

## **5.2 CIS Controls Mapping**

This subsection provides explicit mapping to CIS Controls v8, documenting compliance status and implementation evidence for VM security.

| **CIS Control** | **Implementation Status** | **Evidence Location** | **Assessment Date** |
|-----------------|--------------------------|----------------------|-------------------|
| **CIS.1.1** | **Compliant** | Ubuntu 24.04 CIS v8 L2 baseline on all VMs | **2025-07-01** |
| **CIS.2.1** | **Planned** | VM inventory and configuration management | **TBD** |
| **CIS.4.1** | **Planned** | Network segmentation and access control validation | **TBD** |

**Reference**: [CIS Ubuntu 24.04 Implementation](https://github.com/Pxomox-Astronomy-Lab/proxmox-astronomy-lab/tree/main/docs/Compliance-Security/CIS-Implementation-Guides/Linux/Ubuntu-24-04-Server)

## **5.3 Framework Compliance**

This subsection demonstrates how VM security controls satisfy requirements across multiple compliance frameworks.

VM security infrastructure aligns with CIS Controls v8 baseline, NIST RMF for AI framework, ISO 27001 information security management, and NIST cybersecurity framework through systematic implementation of virtualization security, access controls, and monitoring procedures appropriate for scientific computing environments and astronomical data analysis.

# 💾 **6. Backup & Recovery**

This section documents VM-specific backup strategies and recovery procedures for virtual infrastructure protection.

## **6.1 Protection Strategy**

This subsection details backup approaches and data protection strategies for VM infrastructure and scientific computing environments.

VM backup strategy encompasses systematic VM snapshot and configuration backup through Proxmox Backup Server, application data backup including database and analysis results, configuration management backup for rapid VM restoration, and systematic integration with infrastructure backup procedures ensuring complete VM and data protection.

| **VM Component** | **Backup Strategy** | **Recovery Objective** | **Validation Frequency** |
|------------------|-------------------|----------------------|-------------------------|
| **VM State and Configuration** | **Daily snapshots with retention** | **RTO: 2 hours, RPO: 24 hours** | **Weekly** |
| **Database Data** | **Integrated PostgreSQL backup** | **RTO: 4 hours, RPO: 24 hours** | **Daily** |
| **Analysis Results** | **File-level backup with versioning** | **RTO: 1 hour, RPO: 24 hours** | **Daily** |

## **6.2 Recovery Procedures**

This subsection provides VM recovery processes and infrastructure restoration procedures.

VM recovery procedures include systematic VM restoration from snapshots, application data recovery with integrity validation, configuration restoration with functionality testing, and comprehensive system validation ensuring complete VM functionality and scientific analysis capability following recovery operations.

# 📚 **7. References & Related Resources**

This section provides comprehensive links to related documentation and supporting resources for VM specification implementation and infrastructure management.

## **7.1 Internal References**

| **Document Type** | **Document Title** | **Relationship** | **Link** |
|-------------------|-------------------|------------------|----------|
| **Infrastructure** | Infrastructure Overview | Overall infrastructure architecture and VM context | [README.md](README.md) |
| **Database** | Database Infrastructure | PostgreSQL deployment and optimization requirements | [database/README.md](database/README.md) |
| **Deployment** | Deployment Infrastructure | VM provisioning and configuration procedures | [deployment/README.md](deployment/README.md) |
| **Architecture** | Project Architecture | System design and resource requirements | [../docs/project-architecture.md](../docs/project-architecture.md) |

## **7.2 External Standards**

- **[Proxmox VE Documentation](https://pve.proxmox.com/pve-docs/)** - Virtualization platform administration and VM management guides
- **[PostgreSQL Hardware Requirements](https://www.postgresql.org/docs/current/runtime-config-resource.html)** - Database server resource planning and optimization guidelines
- **[Ubuntu Server Guide](https://ubuntu.com/server/docs)** - Operating system configuration and optimization for scientific computing
- **[CIS Controls v8](https://www.cisecurity.org/controls/)** - Cybersecurity framework for virtualized infrastructure

# ✅ **8. Approval & Review**

This section documents the formal review and approval process for VM specifications documentation.

## **8.1 Review Process**

VM specifications documentation review follows systematic validation of resource allocation, performance requirements, and infrastructure design to ensure effective VM deployment and scientific computing capability.

## **8.2 Approval Matrix**

| **Reviewer** | **Role/Expertise** | **Review Date** | **Approval Status** | **Comments** |
|-------------|-------------------|----------------|-------------------|--------------|
| [Infrastructure Engineer] | VM resource planning and virtualization architecture | 2025-07-01 | **Approved** | VM specifications provide comprehensive resource allocation framework |
| [Database Administrator] | Database server resource requirements and optimization | 2025-07-01 | **Approved** | Database VM specifications support optimal PostgreSQL performance |
| [System Administrator] | VM deployment and operational management procedures | 2025-07-01 | **Approved** | VM specifications enable systematic deployment and reliable operations |

# 📜 **9. Documentation Metadata**

This section provides comprehensive information about VM specifications documentation creation and maintenance.

## **9.1 Change Log**

| **Version** | **Date** | **Changes** | **Author** | **Review Status** |
|------------|---------|-------------|------------|------------------|
| 1.0 | 2025-07-01 | Initial VM specifications with comprehensive resource allocation and configuration details | VintageDon | **Approved** |

## **9.2 Authorization & Review**

VM specifications documentation reflects comprehensive infrastructure design validated through expert review and technical consultation for DESI cosmic void analysis requirements and scientific computing optimization.

## **9.3 Authorship Details**

**Human Author:** VintageDon (Project Lead and Architect)  
**AI Contributor:** Anthropic Claude 4 Sonnet (claude-4-sonnet-20250514)  
**Collaboration Method:** Request-Analyze-Verify-Generate-Validate (RAVGV)  
**Human Oversight:** Complete VM specifications review and validation of resource allocation accuracy

## **9.4 AI Collaboration Disclosure**

This document was collaboratively developed to establish comprehensive VM specifications that enable systematic infrastructure deployment and effective scientific computing for DESI cosmic void research.

---

**🤖 AI Collaboration Disclosure**

This document was collaboratively developed using the Request-Analyze-Verify-Generate-Validate (RAVGV) methodology. The VM specifications documentation reflects systematic infrastructure design development informed by virtualization best practices and scientific computing requirements. All content has been thoroughly reviewed, validated, and approved by qualified human subject matter experts. The human author retains complete responsibility for specification accuracy and infrastructure design effectiveness.

*Generated: 2025-07-01 | Human Author: VintageDon | AI Assistant: Claude 4 Sonnet | Review Status: Approved | Document Version: 1.0*
