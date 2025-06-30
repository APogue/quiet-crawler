---
title: Codebook with Integrated Protocols V2
layout: project_default
permalink: /projects/codebook_w_coding_proto_v2/
---

## VARIABLE-SPECIFIC DEFINITIONS AND PROTOCOLS

### METADATA & UTILITY FIELDS

#### `incident_id` 
**Definition:** Globally unique identifier for each incident (e.g., `INC-001`)

#### `date`
**Definition:** Date the incident occurred (`YYYY-MM-DD`)

#### `source_ids` 
**Definition:** List of internal source references used for incident documentation  
→ Format: `[DB-001, ADM-014]`

#### `keywords`
**Definition:** Internal-use incident tags for filtering and scrape  
→ Format: `[task-force, encampment]`

### BINARY/BOOLEAN VARIABLES

#### `org_affiliated_actor`
**Definition:** Was the actor affiliated with either a UCLA student org or USAC?  
→ `true`, `false`  

#### Coding Protocol 
- Do not proceed to next variable until ALL coding protocol steps have been completed 

#### STEP 1: Evidence Collection
- Flag ALL organizational activity found in sources

 YES/NO

#### STEP 3: FALSE condition check
- If NO evidence references THE SPECIFIC INCIDENT, then code `false`

#### STEP 4: TRUE Condition Check
For each piece of evidence that references the SPECIFIC INCIDENT, check against TRUE conditions and PRINT your answers:
- **Condition A:** "Org member quoted/claimed responsibility/hosted/sponsored THE SPECIFIC INCIDENT" - YES/NO
- **Condition B:** "Org publicly endorsed/amplified THE SPECIFIC INCIDENT" - YES/NO  
- **Condition C:** "Org social media post depicts/shows/references THE SPECIFIC INCIDENT" - YES/NO
- **Condition D:** "Org claimed responsibility for THE SPECIFIC INCIDENT after the fact" - YES/NO
- **Condition E:** "Org made statements supporting THE SPECIFIC INCIDENT specifically" - YES/NO

- **REMEMBER:** Endorsement != 1. incident occurred AT org event but no separate org support for THE SPECIFIC INCIDENT or 2. org supported general event but not THE SPECIFIC INCIDENT

#### STEP 5: Final Decision
- If NO TRUE conditions = YES, then code `false`
- If ANY TRUE condition = YES, then code `true`

#### `actor_student`
**Definition:** Was the actor a student at UCLA?     
→ `true`, `false`  

#### **Coding Protocol:**
- Do not proceed to next variable until ALL coding protocol steps have been completed 

#### STEP 1: Evidence Collection
- Flag source content that mentions any non-affiliation by actors or parties involved with the incident 

#### STEP 2: Incident Boundary Check
- Does the evidence reference THE SPECIFIC INCIDENT described in the incident summary?

#### STEP 3: Final Decision
- Mark `true` if:
  * There is no assertion of non-affiliation by any source
  * If status is ambiguous but no assertion of non-affiliation exists, default to `true`
- Mark `false` ONLY if:
  * A source explicitly identifies the actor as non-student (e.g., "outside agitator," "non-affiliate")

- **REMEMBER:** It is NOT necessary to find explicit evidence of student status if there's no assertion of non-affiliation




