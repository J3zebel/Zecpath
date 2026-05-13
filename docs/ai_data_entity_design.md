# AI Data Entity Design Document

## Overview

This document outlines the standard data entities identified after analyzing structural patterns from technical and non-technical domains (including IT, Healthcare, Finance, Sales, Marketing, and Operations). By standardizing the representations of skills, experience, and educational background, these schemas enable the AI to deeply understand hiring data and perform high-accuracy matching between a candidate's resume and a job description.

## Core Entities Identified

### 1. Skill Object
Skills are the foundational mapping unit between candidates and roles. Since skills can be nuanced, they are categorized and graded.
- **name**: The primary skill name (e.g., "Python", "B2B Sales").
- **level**: Self-assessed or inferred proficiency (Beginner, Intermediate, Advanced, Expert).
- **years_of_experience**: Numeric metric tracking the tenure using a skill.
- **category**:
  - `Hard Skill`: Directly measurable technical or domain-specific abilities.
  - `Soft Skill`: Interpersonal and communication abilities.
  - `Tool`: Software or machinery operated by the candidate.
  - `Framework`: Specific systems/frameworks (e.g., "React", "Spring Boot").
  - `Domain`: Broad industry knowledge (e.g., "Healthcare Compliance").

### 2. Experience Object
The experience object records the employment trajectory, converting raw text paragraphs into quantifiable data points.
- **company_name**: Employer name.
- **designation**: Job title held.
- **start_date / end_date**: Time boundary of the role. Supports calculating tenure.
- **is_current**: Flag for active roles.
- **location**: Geographical location of the role.
- **responsibilities**: Array of distinct tasks handled.
- **achievements**: Array of measurable outcomes (e.g., "Increased sales by 20%").
- **skills_used**: Array of skill names explicitly utilized in this role to provide context to the *Skill Object*.

### 3. Education Structure
Represents academic background and formal learning.
- **institution**: Name of the school or university.
- **degree**: Type of degree earned (e.g., "BS", "MBA").
- **field_of_study**: Major or specialization.
- **start_date / end_date**: Duration of the study.
- **score**: GPA, percentage, or other grading metric.

### 4. Certification Structure
Represents verifiable credentials distinct from formal degrees.
- **name**: Title of the certificate.
- **issuer**: Organization granting the certification (e.g., "AWS", "Google").
- **issue_date / expiration_date**: Validity period of the credential.
- **credential_id**: Unique identifier for verification.

## Implementation Details

These standard data entities have been directly mapped to two core JSON Schemas:
1. **Resume Schema (`schemas/resume_schema.json`)**: Converts a candidate's unstructured CV into a standard `Candidate Profile`.
2. **Job Description Schema (`schemas/jd_schema.json`)**: Converts an employer's unstructured JD into a standard `Job Profile`.

By utilizing these identical base structures (such as `skills` and `mandatory_skills` sharing the same properties), the `ats_engine` and `screening_ai` modules can easily perform vector similarity matching, boolean filtering, and automated scoring of candidates.
