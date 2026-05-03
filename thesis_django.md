# AIRCRAFT TEST FAULT CLOSED-LOOP MANAGEMENT SYSTEM

## Thesis Draft Reference Based on `Aircraft_Test_Fault_Django`

This file is a working thesis reference prepared from the actual Django project in this folder.  
The purpose is to help align the thesis content with the implemented system rather than with the older PHP/Laravel project template.

## Suggested Thesis Title

**AIRCRAFT TEST FAULT CLOSED-LOOP MANAGEMENT SYSTEM**

Alternative formal title:

**Design and Implementation of an Aircraft Test Fault Closed-Loop Management System Based on Django**

## Suggested Chinese Title

**飞机试飞故障闭环管理系统**

## Project Basis

This thesis should use the implementation in `Aircraft_Test_Fault_Django` as its primary reference.  
Based on the current codebase, the system is a web-based management platform used to record, monitor, analyze, and close aircraft test faults through a structured workflow.

## Actual Technology Stack Used in This Project

- Backend framework: Django
- Programming language: Python
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript
- UI library: Bootstrap
- Data visualization: Chart.js
- Authentication: Django authentication system
- AI integration: OpenRouter API with local fallback logic

## Core Applications in the Project

The Django project is divided into several applications:

- `accounts`: user authentication and role management
- `aircraft`: aircraft master data management
- `faults`: fault creation, editing, tracking, and workflow control
- `dashboard`: statistics and operational overview
- `reports`: filtered reporting and summary analysis
- `ai_tools`: AI-assisted fault description and explanation

## Main Functions Implemented

### 1. User Management

The system provides login, registration, logout, and user administration functions.  
It supports multiple user roles, including:

- Admin
- Test Engineer
- Maintenance Engineer
- Test Manager

The role mechanism is used to control access to important features such as aircraft management, user administration, and fault workflow operations.

### 2. Aircraft Management

The aircraft module stores the master data of aircraft involved in testing and maintenance activities.  
Each aircraft record includes:

- Tail number
- Model
- Manufacturer
- Current status

This module helps connect each fault record to a specific aircraft.

### 3. Fault Management

The fault module is the core of the system.  
Users can create, view, update, and delete fault records based on role permissions.

Each fault record stores operational and technical information such as:

- Fault title
- Fault description
- Aircraft
- Subsystem
- Severity
- Assigned engineer
- Flight phase
- Component affected
- Environmental conditions
- Analysis findings
- Root cause
- Resolution action
- Severity score
- Resolution time
- AI explanation

### 4. Closed-Loop Workflow Management

This project implements a closed-loop workflow for aircraft fault handling.  
The workflow status is managed using controlled transitions:

`New -> Assigned -> Under Analysis -> Root Cause Identified -> Fix In Progress -> Resolved -> Verified Closed`

This workflow ensures that each fault progresses through a logical engineering process from initial reporting to final verification and closure.

### 5. Status History Tracking

The system records each valid fault status transition in a dedicated status history table.  
This feature provides traceability and accountability by storing:

- previous status
- new status
- changed by
- notes
- timestamp

This supports auditing and analysis of the maintenance process.

### 6. Dashboard and Visualization

The dashboard module provides a visual summary of operational data.  
It includes metrics and charts such as:

- total faults
- open faults
- overdue faults
- closure rate
- resolved faults
- critical faults
- fault distribution by subsystem
- fault distribution by flight phase
- aircraft hotspots
- recent activity

These visual summaries help users monitor the current state of aircraft test fault handling.

### 7. Reporting

The reports module allows filtering fault records by:

- status
- severity
- aircraft
- date range

It also provides aggregated views such as:

- faults by aircraft
- faults by subsystem
- severity breakdown
- recent fault records

### 8. AI Assistance

The system includes an AI helper module that supports:

- generating initial fault descriptions
- generating fault explanations

When the external AI service is not available, the system falls back to local template-based responses.  
This improves usability while maintaining system availability.

## Suggested Abstract

This thesis presents the design and implementation of an Aircraft Test Fault Closed-Loop Management System developed to improve the recording, tracking, analysis, and resolution of aircraft test faults. In aircraft testing and maintenance environments, fault information must be handled accurately and efficiently to support operational safety, technical investigation, and timely corrective action. Traditional manual or fragmented fault recording methods may lead to delays, inconsistent status tracking, and difficulty in monitoring fault progress. To address these issues, this project develops a web-based management system that integrates user management, aircraft management, fault tracking, reporting, dashboard analytics, and AI-assisted support into a unified platform.

The system is implemented using Django as the backend framework and PostgreSQL as the database. The frontend is built with HTML, CSS, JavaScript, and Bootstrap, while Chart.js is used for visual data presentation. The system adopts a role-based access control mechanism that supports several operational roles, including administrator, test engineer, maintenance engineer, and test manager. The core function of the platform is the closed-loop fault workflow, which manages each fault through the stages of New, Assigned, Under Analysis, Root Cause Identified, Fix In Progress, Resolved, and Verified Closed. To improve traceability, each workflow update is recorded in a status history module.

In addition to basic fault management, the system provides dashboards and reports for monitoring fault statistics, aircraft hotspots, severity distribution, and recent maintenance activity. The project also integrates an AI support module capable of generating concise fault descriptions and explanatory maintenance summaries. When external AI access is unavailable, the system uses local fallback logic to ensure continuity of service.

The implementation and testing results show that the system can support structured aircraft fault management more effectively than unorganized recording methods. It improves visibility, traceability, and operational coordination during the aircraft test fault handling process. The developed system demonstrates practical value as a digital management platform for aircraft fault lifecycle control and offers a foundation for future expansion in predictive maintenance and intelligent decision support.

**Keywords:** aircraft test fault; closed-loop management; Django; PostgreSQL; workflow tracking

## Suggested Chinese Abstract

本文设计并实现了一套飞机试飞故障闭环管理系统，旨在提高飞机试飞故障在记录、跟踪、分析和处置过程中的规范性与效率。在飞机试飞和维护场景中，故障信息需要被准确、及时地处理，以保障运行安全、支持技术分析并推动纠正措施的落实。传统的人工记录方式或分散式管理方式容易造成信息更新滞后、状态跟踪不清晰以及故障处理过程难以统一管理等问题。为解决上述问题，本文基于实际项目开发了一套集用户管理、飞机管理、故障管理、报表分析、可视化看板以及智能辅助功能于一体的 Web 管理系统。

本系统采用 Django 作为后端开发框架，PostgreSQL 作为数据库，前端使用 HTML、CSS、JavaScript 和 Bootstrap 实现，图表展示采用 Chart.js。系统采用基于角色的权限控制机制，支持管理员、试飞工程师、维修工程师和试飞经理等不同角色。系统核心功能是故障闭环工作流管理，即将故障处理过程划分为 New、Assigned、Under Analysis、Root Cause Identified、Fix In Progress、Resolved 和 Verified Closed 等阶段，并通过状态历史记录模块对每次状态变更进行跟踪，从而提高故障处理过程的可追溯性和可管理性。

除基本故障管理外，系统还提供仪表板与报表模块，用于展示故障总数、未关闭故障、逾期故障、严重程度分布、子系统热点以及近期活动等关键数据。同时，系统集成了智能辅助模块，可用于自动生成故障描述和故障解释内容；当外部 AI 服务不可用时，系统仍可通过本地回退逻辑生成基础说明，从而保证功能连续性。

系统实现与测试结果表明，该平台能够较好地支持飞机试飞故障从发现、分派、分析、修复到关闭验证的全过程管理。与传统记录方式相比，本系统在可视化、可追踪性和协同效率方面具有明显提升，可为飞机试飞故障生命周期管理提供有效的信息化支撑，并为后续扩展到预测性维护和智能决策支持提供基础。

**关键词：** 飞机试飞故障；闭环管理；Django；PostgreSQL；工作流跟踪

## Suggested Chapter Structure

### Chapter 1 Introduction

- project background
- problem statement
- project objectives
- scope of the system
- significance of the project

### Chapter 2 Technology Background

- Python and Django
- PostgreSQL
- HTML, CSS, JavaScript
- Bootstrap
- Chart.js
- role-based access control
- AI service integration

### Chapter 3 System Analysis and Design

- system architecture
- functional module design
- workflow design
- database design
- user roles and permissions
- UI structure

### Chapter 4 System Implementation and Testing

- implementation of user management
- implementation of aircraft management
- implementation of fault management
- implementation of workflow status tracking
- implementation of dashboard and reports
- implementation of AI helper
- unit and functional testing

### Conclusion

- project achievements
- limitations
- future improvements

## Suggested Database Entities

### UserProfile

- user
- role

### Aircraft

- tail_number
- model
- manufacturer
- current_status

### Fault

- title
- description
- aircraft
- reported_by
- assigned_to
- subsystem
- severity
- current_status
- reported_date
- closed_date
- closed_by
- analysis_findings
- root_cause
- resolution_action
- severity_score
- resolution_time_hours
- component_affected
- environmental_conditions
- flight_phase
- ai_explanation

### StatusHistory

- fault
- old_status
- new_status
- changed_by
- change_notes
- change_timestamp

## Notes for Replacing the Old Thesis Content

The old thesis text about:

- PHP
- Laravel
- MySQL
- XAMPP
- literature management
- source code library for research
- research topic management

should be replaced because it does not match the current Django project.

The updated thesis should instead describe the actual project features implemented in this folder.

## Source Files Used as Reference

- `config/settings.py`
- `accounts/models.py`
- `accounts/views.py`
- `aircraft/models.py`
- `aircraft/views.py`
- `faults/models.py`
- `faults/views.py`
- `faults/services.py`
- `dashboard/views.py`
- `reports/views.py`
- `ai_tools/views.py`
- `accounts/tests.py`
- `faults/tests.py`
- `reports/tests.py`
- `ai_tools/tests.py`

## Next Step

If needed, this file can be expanded into:

- a complete Chapter 1 draft
- a complete Chapter 2 draft
- a complete Chapter 3 draft
- a complete Chapter 4 draft
- a full thesis version in English
- a bilingual English and Chinese thesis draft
