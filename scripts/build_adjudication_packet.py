"""
MoSPI ACBP to KCM Competency Mapping Human Adjudication Packet Builder (Stage 3.4.2).

Constructs the comprehensive human-adjudication package for the 26-case benchmark.
Adheres strictly to the 6-question adjudication decision process:
  1. Course identity: Exact course, related course, or general subject.
  2. Subject coverage: Specific topics supported by authentic evidence.
  3. Competency alignment: Precise KCM definition and behavioral sub-theme match.
  4. Evidence sufficiency: Evaluation of evidence completeness.
  5. Competency depth: Stated learning objectives, assessment, and mastery limitations.
  6. Final benchmark label: Justified benchmark label under the approved taxonomy.

Outputs:
  - data/interim/mapping_adjudication_packet.json
  - data/interim/mapping_adjudication_packet.csv
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input paths
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
LEDGER_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_ledger.json"
AUDIT_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_provenance_audit.json"
COURSES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
EVIDENCE_PACK_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_evidence_pack.json"

# Output paths
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PACKET_JSON_PATH = INTERIM_DIR / "mapping_adjudication_packet.json"
PACKET_CSV_PATH = INTERIM_DIR / "mapping_adjudication_packet.csv"

# Immutable source hashes
EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"

# Detailed case-by-case adjudication guidance specifications
CASE_ADJUDICATION_SPECS: Dict[str, Dict[str, Any]] = {
    "BM-CASE-001": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. High-level CBC mandate covers collaborative governance, but local lesson plan is unmirrored.",
        "q2_subject_coverage": "Collaborative governance in public service; institutional partnership mechanisms.",
        "q3_competency_alignment": "Candidate KCM-BEH-06 (Collaboration) definition matches 'Working in tandem with others as an integral unit...', specifically Relationship Management and Knowledge Sharing sub-themes.",
        "q4_evidence_sufficiency": "Insufficient. Course metadata and title match verified, but lack of granular syllabus precludes behavioral verification.",
        "q5_competency_depth": "Duration is 1 hour 00 minutes 44 seconds. No evidence on interactive exercises, simulations, or behavioral assessment criteria.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Course title explicitly references 'Collaboration'; provider is CBC (author of KCM framework); targeted at apex executive leadership.",
        "counter_evidence_and_limitations": "Restricted behind civil service Parichay SSO; cannot prove whether course teaches deep behavioral indicators or merely conceptual awareness.",
        "alternative_kcm_candidates": "KCM-BEH-10 (Strategic Leadership), KCM-BEH-11 (Collaborative Leadership)",
        "sme_adjudication_questions": "Does a 1-hour online module impart observable behavioral collaboration for apex officers (DDG/JS+), or does it serve as an awareness briefing?",
    },
    "BM-CASE-002": {
        "q1_course_identity": "ATI Mysuru executive modules cover public project leadership, matching the general topic, but the exact 17m 58s iGOT module is unmirrored.",
        "q2_subject_coverage": "Project leadership, team steering, and outcome monitoring in development programmes.",
        "q3_competency_alignment": "Partial and ambiguous. 'Leadership' suggests KCM-BEH-10 (Strategic Leadership) or KCM-BEH-12 (Team Leadership), while 'Project Management' aligns with KCM-FUNC-05 (Project Management).",
        "q4_evidence_sufficiency": "Insufficient. 18-minute runtime is inadequate to prove functional competency development.",
        "q5_competency_depth": "Severe Limitation: An 18-minute micro-module cannot impart technical project management (PERT/CPM, GFR appraisal, risk register).",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Title contains 'Project Management' and provider is an official state Administrative Training Institute.",
        "counter_evidence_and_limitations": "Very brief runtime (17m 58s). Combines behavioral ('Leadership') and functional ('Project Management') domains.",
        "alternative_kcm_candidates": "KCM-BEH-10 (Strategic Leadership), KCM-BEH-12 (Team Leadership)",
        "sme_adjudication_questions": "Should an 18-minute module be mapped to a complex functional competency like KCM-FUNC-05, or should micro-modules below 30 minutes be classified under behavioral awareness or rejected as insufficient for competency acquisition?",
    },
    "BM-CASE-003": {
        "q1_course_identity": "CBC Indic Leadership framework verified via public executive collaborations (IIM Calcutta), but specific 1h 09m iGOT lesson plan is unverified and behind SSO.",
        "q2_subject_coverage": "Indic statecraft, ethical leadership, civilizational governance principles (Rajadharma, Arthashastra).",
        "q3_competency_alignment": "Aligns conceptually with KCM-BEH-10 (Strategic Leadership) sub-themes: Strategic Direction, Visioning, and Value-Driven Governance.",
        "q4_evidence_sufficiency": "Insufficient. High-level framework verified, but session outline unverified.",
        "q5_competency_depth": "Limitation: 1-hour conceptual module; lacks evidence on strategic execution or simulation-based assessment.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Developed under CBC Karmayogi leadership series; title explicitly targets Strategic Leadership.",
        "counter_evidence_and_limitations": "Traditional civilizational frameworks may not map cleanly onto modern public administration strategic planning indicators without lesson plan inspection.",
        "alternative_kcm_candidates": "KCM-BEH-02 (Personal Effectiveness), KCM-BEH-01 (Self-Awareness - Purposefulness)",
        "sme_adjudication_questions": "To what extent does 'Indic Way' statecraft satisfy the modern bureaucratic metrics of KCM-BEH-10 (e.g. multi-year departmental roadmapping, KPIs)?",
    },
    "BM-CASE-004": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. Cross-cadre delivery to Director / JD level. Same CBC course asset as BM-CASE-001.",
        "q2_subject_coverage": "Collaborative governance in public service; institutional partnership mechanisms.",
        "q3_competency_alignment": "Candidate KCM-BEH-06 (Collaboration) definition matches 'Working in tandem with others as an integral unit...', specifically Relationship Management and Knowledge Sharing sub-themes.",
        "q4_evidence_sufficiency": "Insufficient. Course metadata verified, but lack of granular syllabus precludes behavioral verification.",
        "q5_competency_depth": "Duration 01.00.44. No assessment criteria or learning outcomes verified locally.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Course title explicitly references 'Collaboration'; provider is CBC.",
        "counter_evidence_and_limitations": "Restricted behind Parichay SSO; cross-cadre differentiation unverified.",
        "alternative_kcm_candidates": "KCM-BEH-10 (Strategic Leadership), KCM-BEH-11 (Collaborative Leadership)",
        "sme_adjudication_questions": "Does the Director/JD cadre delivery differ in syllabus or proficiency expectation from the DDG/JS+ delivery, or is it an identical digital asset?",
    },
    "BM-CASE-005": {
        "q1_course_identity": "CBC Indic Leadership series delivered to DS / US middle management. High-level framework verified, but session plan is unverified and behind SSO.",
        "q2_subject_coverage": "Indic governance ethics, Rajadharma, administrative decision-making.",
        "q3_competency_alignment": "Candidate KCM-BEH-10 (Strategic Leadership) title matches, but applicability to middle management operational roles is debatable.",
        "q4_evidence_sufficiency": "Insufficient. Course syllabus unverified locally.",
        "q5_competency_depth": "Duration 01.09.28. No formative or summative assessment details available.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Part of CBC flagship leadership series; title contains 'Strategic Leadership'.",
        "counter_evidence_and_limitations": "Cadre DS/US rarely exercises ministry-wide strategic leadership; duties focus on branch administration and file movement.",
        "alternative_kcm_candidates": "KCM-BEH-05 (Outcome Orientation), KCM-BEH-13 (Decision Making)",
        "sme_adjudication_questions": "Is Strategic Leadership an appropriate competency target for DS/US officers whose duties are primarily operational/supervisory, or should this map to Decision Making or Team Leadership?",
    },
    "BM-CASE-006": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. Delivered to DS / US cadre. Same CBC course asset as BM-CASE-001 and BM-CASE-004.",
        "q2_subject_coverage": "Collaborative governance in public service; institutional partnership mechanisms.",
        "q3_competency_alignment": "Candidate KCM-BEH-06 (Collaboration) matches title and high-level CBC mandate.",
        "q4_evidence_sufficiency": "Insufficient. Granular syllabus restricted behind SSO.",
        "q5_competency_depth": "Duration 01.00.44. No practice exercises or workplace assessment verified.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Title contains 'Collaboration'; official CBC course asset.",
        "counter_evidence_and_limitations": "SSO access restriction prevents verification of learning depth.",
        "alternative_kcm_candidates": "KCM-BEH-11 (Collaborative Leadership), KCM-BEH-06 (Collaboration)",
        "sme_adjudication_questions": "Should identical course assets delivered across three distinct cadre tiers (DDG, Director, DS/US) receive the same competency mapping or differentiated proficiency levels?",
    },
    "BM-CASE-007": {
        "q1_course_identity": "MDNIY Common Yoga Protocol represents authentic apex institutional curriculum, but not the exact 45-minute iGOT video course.",
        "q2_subject_coverage": "Yogic postures (Asanas), breathing practices (Pranayama), relaxation techniques, stress alleviation, holistic lifestyle health.",
        "q3_competency_alignment": "Very weak civil service alignment. Distantly touches KCM-BEH-01 (Self-Awareness: Self-Analysis) or KCM-BEH-02 (Personal Effectiveness: Stress Management), but wellness is personal health rather than administrative competency.",
        "q4_evidence_sufficiency": "Sufficient for institutional wellness curriculum; insufficient for civil service competency mapping.",
        "q5_competency_depth": "Physical postures and health protocol; zero public administration or statistical governance outcomes.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "MDNIY is the national apex yoga institute; recognized under Ministry of Ayush.",
        "counter_evidence_and_limitations": "Personal physical health and yoga practices do not constitute core civil service behavioral competencies under KCM.",
        "alternative_kcm_candidates": "KCM-BEH-01 (Self-Awareness), KCM-BEH-02 (Personal Effectiveness), or no_applicable_kcm_competency (Wellness Gap)",
        "sme_adjudication_questions": "Should wellness and health courses in ACBP be classified as outside KCM scope (no_applicable_kcm_competency), or mapped to Self-Awareness / Personal Effectiveness?",
    },
    "BM-CASE-008": {
        "q1_course_identity": "LBSNAA executive modules on Emotional Intelligence exist; exact iGOT course is behind Parichay SSO.",
        "q2_subject_coverage": "Self-regulation, empathy, emotional awareness in public administration, stress coping mechanisms.",
        "q3_competency_alignment": "Crucial finding: KCM 2024 has NO standalone 'Emotional Intelligence' competency. Relevant indicators reside under KCM-BEH-01 (Self-Awareness: Self-Analysis, Self-Confidence) and KCM-BEH-02 (Personal Effectiveness: Emotional Regulation).",
        "q4_evidence_sufficiency": "Insufficient. Course syllabus not available locally.",
        "q5_competency_depth": "Duration is 45m 12s. No assessment or practice modules verified.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "LBSNAA is the premier civil service training academy; subject is highly relevant to public administration ethics.",
        "counter_evidence_and_limitations": "SSO access restriction; absence of an explicit 'Emotional Intelligence' competency in KCM 2024 requires mapping to proxy competencies.",
        "alternative_kcm_candidates": "KCM-BEH-01 (Self-Awareness), KCM-BEH-02 (Personal Effectiveness), KCM-BEH-06 (Collaboration)",
        "sme_adjudication_questions": "Since KCM 2024 omits a dedicated Emotional Intelligence competency, which sub-theme (Self-Awareness vs Personal Effectiveness vs Collaborative Leadership) should be designated as primary?",
    },
    "BM-CASE-009": {
        "q1_course_identity": "MDNIY stress protocols cover the topic; exact 30-minute iGOT video course is behind SSO.",
        "q2_subject_coverage": "Stress identification, relaxation techniques, mindful breathing, coping strategies in workplace environments.",
        "q3_competency_alignment": "Relevant to KCM-BEH-01 (Self-Awareness: Self-Analysis) and KCM-BEH-02 (Personal Effectiveness: Resilience / Emotional Balance).",
        "q4_evidence_sufficiency": "Insufficient. Exact iGOT module outline unverified.",
        "q5_competency_depth": "Duration is only 30 minutes; introductory awareness only.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "MDNIY official institutional protocols verify stress management techniques.",
        "counter_evidence_and_limitations": "Brief duration (30 mins); overlaps between personal wellness and professional effectiveness.",
        "alternative_kcm_candidates": "KCM-BEH-01 (Self-Awareness), KCM-BEH-02 (Personal Effectiveness)",
        "sme_adjudication_questions": "Does stress management qualify as civil service Personal Effectiveness (KCM-BEH-02) or is it an extracurricular employee assistance topic?",
    },
    "BM-CASE-010": {
        "q1_course_identity": "ISTM executive curriculum covers workplace conflict resolution; exact 45-minute iGOT module is behind SSO.",
        "q2_subject_coverage": "Sources of interpersonal conflict, mediation techniques, negotiation, de-escalation in government offices.",
        "q3_competency_alignment": "Aligns with KCM-BEH-06 (Collaboration: Relationship Management) or KCM-BEH-11 (Collaborative Leadership: Conflict Resolution sub-theme) or KCM-BEH-12 (Team Leadership).",
        "q4_evidence_sufficiency": "Insufficient. Granular lesson plan unverified locally.",
        "q5_competency_depth": "Duration 45 minutes; lacks evidence on practical negotiation role-plays.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "ISTM is the apex central secretariat institute; conflict resolution is a recognized administrative skill.",
        "counter_evidence_and_limitations": "SSO access restriction prevents verification of specific behavioral indicators.",
        "alternative_kcm_candidates": "KCM-BEH-06 (Collaboration), KCM-BEH-11 (Collaborative Leadership), KCM-BEH-12 (Team Leadership)",
        "sme_adjudication_questions": "For Director/JD level, should Conflict Resolution map to operational Collaboration (KCM-BEH-06) or Team Leadership (KCM-BEH-12)?",
    },
    "BM-CASE-011": {
        "q1_course_identity": "ISTM time management guidelines cover the topic; exact 30-minute iGOT module is behind SSO.",
        "q2_subject_coverage": "Prioritization, task delegation, eliminating time wasters, diary management, deadline adherence.",
        "q3_competency_alignment": "Aligns with KCM-BEH-02 (Personal Effectiveness: Time Management sub-theme) or KCM-BEH-08 (Operational Excellence: Planning & Organizing).",
        "q4_evidence_sufficiency": "Insufficient. Module outline unverified locally.",
        "q5_competency_depth": "Duration is only 30 minutes; cannot establish habitual behavioural mastery.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "ISTM official secretarial training covers office time management.",
        "counter_evidence_and_limitations": "Brief duration; lacks assessment of personal productivity systems.",
        "alternative_kcm_candidates": "KCM-BEH-02 (Personal Effectiveness), KCM-BEH-08 (Operational Excellence)",
        "sme_adjudication_questions": "Does a 30-minute time management module justify mapping to Personal Effectiveness or Operational Excellence for supervisory officers (SSO/SO)?",
    },
    "BM-CASE-012": {
        "q1_course_identity": "ISTM foundational secretariat materials cover interpersonal communication; exact 45-minute module is behind SSO.",
        "q2_subject_coverage": "Active listening, constructive feedback, verbal and non-verbal communication, working in teams.",
        "q3_competency_alignment": "Aligns with KCM-BEH-04 (Communication) or KCM-BEH-06 (Collaboration).",
        "q4_evidence_sufficiency": "Insufficient. Exact session outline unverified locally.",
        "q5_competency_depth": "Duration 45 minutes. No behavioral simulation or peer review evidence.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "ISTM is authoritative provider for secretarial interpersonal training.",
        "counter_evidence_and_limitations": "SSO access restriction; potential overlap between Communication and Collaboration.",
        "alternative_kcm_candidates": "KCM-BEH-04 (Communication), KCM-BEH-06 (Collaboration)",
        "sme_adjudication_questions": "For junior statistical and secretariat officers (JSO/ASO), should Interpersonal Skills be mapped primarily to Communication (KCM-BEH-04) or Collaboration (KCM-BEH-06)?",
    },
    "BM-CASE-013": {
        "q1_course_identity": "ISTM classroom curriculum on Disciplinary Proceedings provides authentic apex institutional evidence, but exact 75-minute iGOT course is unmirrored.",
        "q2_subject_coverage": "CCS (CCA) Rules 1965, charge sheeting, inquiry officer and presenting officer procedures, statutory penalties, vigilance clearance.",
        "q3_competency_alignment": "Direct topic alignment to KCM-FUNC-17 (Vigilance Administration) definition and disciplinary inquiry sub-themes.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "75-minute runtime may only cover procedural basics rather than quasi-judicial inquiry mastery.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM Disciplinary Proceedings curriculum verifies comprehensive statutory rule coverage.",
        "counter_evidence_and_limitations": "Disciplinary proceedings require deep quasi-judicial competence; a 75-minute overview cannot certify inquiry officer qualification.",
        "alternative_kcm_candidates": "KCM-FUNC-17 (Vigilance Administration), KCM-FUNC-18 (Litigation Management)",
        "sme_adjudication_questions": "Is a 75-minute iGOT video sufficient to support qualification for Vigilance Administration (KCM-FUNC-17) at DDG level, or should it be restricted to a foundational awareness indicator?",
    },
    "BM-CASE-014": {
        "q1_course_identity": "DoPT / LBSNAA executive public policy modules cover the topic; exact 45-minute module is behind SSO.",
        "q2_subject_coverage": "Evidence-based decision making, policy design, stakeholder consultation, cabinet note synthesis.",
        "q3_competency_alignment": "Direct topic match to KCM-FUNC-02 (Policy Architecture) and KCM-FUNC-03 (Cabinet Note Preparation).",
        "q4_evidence_sufficiency": "Insufficient. Course outline unverified locally.",
        "q5_competency_depth": "Duration is 45 minutes; inadequate to cover complex regulatory impact analysis.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Created by DoPT / LBSNAA for top civil service leadership.",
        "counter_evidence_and_limitations": "SSO access restriction; brief duration for an advanced policy formulation domain.",
        "alternative_kcm_candidates": "KCM-FUNC-02 (Policy Architecture), KCM-FUNC-03 (Cabinet Note Preparation)",
        "sme_adjudication_questions": "Can a 45-minute overview develop policy formulation and cabinet note synthesis (KCM-FUNC-02), or does it merely introduce evidence-based policy concepts?",
    },
    "BM-CASE-015": {
        "q1_course_identity": "AJ-NIFM Union Budget preparation curriculum provides authoritative institutional evidence; exact 60-minute iGOT course is unmirrored.",
        "q2_subject_coverage": "General Financial Rules (GFR), Delegation of Financial Powers Rules (DFPR), Revised Estimates, Budget Estimates, outcome budgeting.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-09 (Financial Management) definition: 'Planning, directing, monitoring, organizing, and controlling of monetary resources...'",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour. No financial modeling or budget drafting exercises verified.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "AJ-NIFM is the Ministry of Finance's premier national financial management institute.",
        "counter_evidence_and_limitations": "1-hour duration covers high-level budget cycle rather than granular expenditure accounting.",
        "alternative_kcm_candidates": "KCM-FUNC-09 (Financial Management)",
        "sme_adjudication_questions": "Does the course develop budget estimation and expenditure control under GFR/DFPR, or is it an executive overview of the annual Union Budget calendar?",
    },
    "BM-CASE-016": {
        "q1_course_identity": "ISTM Manual for Parliamentary Matters provides authentic institutional material; exact 45-minute iGOT course is unmirrored.",
        "q2_subject_coverage": "Parliamentary questions (Starred/Unstarred), legislative bills, parliamentary assurances, standing committee references.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-14 (Handling Parliamentary Matters) definition and sub-themes.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 45 minutes; covers parliamentary procedures without drafting evaluation.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM is the official authority for secretariat parliamentary procedures.",
        "counter_evidence_and_limitations": "Brief duration; SSO restriction on specific quiz/assessment content.",
        "alternative_kcm_candidates": "KCM-FUNC-14 (Handling Parliamentary Matters)",
        "sme_adjudication_questions": "Does the 45-minute session cover assurances, starred/unstarred questions, and legislative drafting to the depth required by KCM-FUNC-14?",
    },
    "BM-CASE-017": {
        "q1_course_identity": "AJ-NIFM Public Procurement Manual and GeM training curriculum verify subject matter; exact 90-minute course is unmirrored.",
        "q2_subject_coverage": "GFR 2017 Chapter 6, GeM portal procurement, bidding documents, reverse auction, contract management.",
        "q3_competency_alignment": "Strong alignment to KCM-FUNC-06 (Public Procurement (GFR)) and secondary alignment to KCM-FUNC-07 (Material Management (GFR)).",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration is 1 hour 30 minutes; covers statutory procurement rules.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "AJ-NIFM is the apex training body for central procurement rules and GeM.",
        "counter_evidence_and_limitations": "Distinction between GFR procurement rules (FUNC-06) and inventory/material management (FUNC-07) must be resolved by examining course modules.",
        "alternative_kcm_candidates": "KCM-FUNC-06 (Public Procurement (GFR)), KCM-FUNC-07 (Material Management (GFR))",
        "sme_adjudication_questions": "Is the primary emphasis on GFR procurement rules (KCM-FUNC-06) or GeM portal operations / inventory control (KCM-FUNC-07)?",
    },
    "BM-CASE-018": {
        "q1_course_identity": "ISTM Brochure on Reservation in Service provides authentic institutional evidence; exact 60-minute iGOT course is unmirrored.",
        "q2_subject_coverage": "Constitutional provisions for SC/ST/OBC/EWS/PwD reservation, post-based rosters, de-reservation procedures, liaison officer duties.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-12 (Establishment & HR) sub-theme on service rules and reservation administration.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour. No roster calculation exercises verified.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM is the national nodal training body for DoPT reservation rosters.",
        "counter_evidence_and_limitations": "1-hour runtime provides conceptual summary of reservation orders rather than practical roster audit competence.",
        "alternative_kcm_candidates": "KCM-FUNC-12 (Establishment & HR)",
        "sme_adjudication_questions": "Does the course develop roster maintenance and post-based reservation administration under KCM-FUNC-12, or is it an informational compliance briefing?",
    },
    "BM-CASE-019": {
        "q1_course_identity": "NeGD Emerging Technologies in Governance curriculum covers the topic; exact 30-minute module is behind SSO.",
        "q2_subject_coverage": "Generative AI principles, LLM applications in public services, prompt crafting, ethical AI governance, data privacy.",
        "q3_competency_alignment": "Aligns with KCM-FUNC-10 (Digital Fluency: Emerging Technologies sub-theme).",
        "q4_evidence_sufficiency": "Insufficient. Course outline unverified locally.",
        "q5_competency_depth": "Duration is 30 minutes; introductory awareness of emerging tech.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "NeGD (MeitY) is the apex agency for digital e-governance initiatives.",
        "counter_evidence_and_limitations": "30-minute duration cannot impart technical prompt engineering or AI system deployment competence.",
        "alternative_kcm_candidates": "KCM-FUNC-10 (Digital Fluency), KCM-FUNC-11 (Data Analytics)",
        "sme_adjudication_questions": "Is Generative AI awareness a sub-theme of Digital Fluency (emerging technologies) or does it require specialized data science competencies?",
    },
    "BM-CASE-020": {
        "q1_course_identity": "NeGD Big Data in Governance curriculum covers public sector big data use cases; exact 46m 21s module is behind SSO.",
        "q2_subject_coverage": "Big data concepts, data-driven governance, analytics infrastructure, public service delivery use cases.",
        "q3_competency_alignment": "Critical finding: ACBP categorized this as 'Domain', but provider is NeGD (MeitY) for generic governance. Aligns with KCM-FUNC-10 (Digital Fluency) or KCM-FUNC-11 (Data Analytics).",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 46 minutes 21 seconds. High-level architecture overview without hands-on querying.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "NeGD official digital governance training framework.",
        "counter_evidence_and_limitations": "Misclassified as 'Domain' in ACBP despite being a generic e-governance technology course.",
        "alternative_kcm_candidates": "KCM-FUNC-10 (Digital Fluency), KCM-FUNC-11 (Data Analytics)",
        "sme_adjudication_questions": "Why did MoSPI classify generic Big Data governance under 'Domain' instead of 'Functional'? Does it map to KCM-FUNC-10 (Digital Fluency) or KCM-FUNC-11 (Data Analytics)?",
    },
    "BM-CASE-021": {
        "q1_course_identity": "NSSTA official statistical system calendar and training manual verify topic; exact 90-minute course is unmirrored.",
        "q2_subject_coverage": "Indian Statistical System architecture, CSO/NSSO merger, Collection of Statistics Act 2008, National Statistical Commission (NSC).",
        "q3_competency_alignment": "Zero direct representation in KCM 2024. KCM contains generic administrative/behavioral competencies but omits official statistical system governance.",
        "q4_evidence_sufficiency": "Sufficient for official statistics domain topic; confirms absence from generic civil service KCM.",
        "q5_competency_depth": "Covers institutional mandates of MoSPI and national statistical coordination.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "NSSTA is the national apex statistical academy under MoSPI.",
        "counter_evidence_and_limitations": "KCM 2024 has no 'Official Statistics' or 'Statistical Legislation' competency.",
        "alternative_kcm_candidates": "no_applicable_kcm_competency (Official Statistics Domain Gap)",
        "sme_adjudication_questions": "Does any generic KCM competency encompass institutional statistical governance, or does this confirm an unrepresented official statistics Domain competency gap?",
    },
    "BM-CASE-022": {
        "q1_course_identity": "NSSTA HCES Survey Manual and Schedule 1.0 verify official survey methodology; exact 2-hour iGOT video is unmirrored.",
        "q2_subject_coverage": "Household Consumption Expenditure Survey (HCES), microdata record layout, Monthly Per Capita Consumer Expenditure (MPCE), sampling multipliers, multi-stage stratified sampling.",
        "q3_competency_alignment": "Dual consideration: Microdata extraction and tabulation share conceptual overlap with KCM-FUNC-11 (Data Analytics). However, survey weighting, NSS sampling designs, and consumption concepts are specialist statistical domain knowledge.",
        "q4_evidence_sufficiency": "Sufficient for survey methodology; insufficient to resolve generic vs domain mapping without expert adjudication.",
        "q5_competency_depth": "Duration 2 hours. Covers unit-level data handling and tabulation.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "NSSTA is the apex national training academy for NSS survey operations.",
        "counter_evidence_and_limitations": "Over-simplified claim of pure domain gap ignores Data Analytics (KCM-FUNC-11) overlap; requires expert adjudication.",
        "alternative_kcm_candidates": "KCM-FUNC-11 (Data Analytics) vs no_applicable_kcm_competency (HCES Survey Domain Gap)",
        "sme_adjudication_questions": "Should HCES microdata handling be mapped to generic Data Analytics (KCM-FUNC-11) or flagged as an official statistics Domain gap?",
    },
    "BM-CASE-023": {
        "q1_course_identity": "NSSTA ASI Survey Manual and microdata documentation verify industrial statistics curriculum; exact 2-hour iGOT course is unmirrored.",
        "q2_subject_coverage": "Annual Survey of Industries (ASI), factory sector frame, NIC-2008 classification, Gross Value Added (GVA), capital formation, multiplier application.",
        "q3_competency_alignment": "Dual consideration: Statistical data manipulation aligns with KCM-FUNC-11 (Data Analytics), but industrial economic accounting and sampling frame maintenance are specialist official statistics knowledge.",
        "q4_evidence_sufficiency": "Sufficient for industrial survey methodology; requires expert adjudication on domain gap vs analytics.",
        "q5_competency_depth": "Duration 2 hours. Focuses on unit-level enterprise data extraction.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "NSSTA official industrial statistics curriculum and survey schedules.",
        "counter_evidence_and_limitations": "Potential overlap with Data Analytics (KCM-FUNC-11) must be evaluated alongside domain-specific economic concepts.",
        "alternative_kcm_candidates": "KCM-FUNC-11 (Data Analytics) vs no_applicable_kcm_competency (ASI Survey Domain Gap)",
        "sme_adjudication_questions": "Should ASI enterprise microdata analysis be mapped to Data Analytics (KCM-FUNC-11) or treated as an official statistics Domain gap?",
    },
    "BM-CASE-024": {
        "q1_course_identity": "CERT-In Cyber Hygiene guidelines cover personal and workstation digital safety; exact 30-minute module is behind SSO.",
        "q2_subject_coverage": "Password hygiene, multi-factor authentication, phishing prevention, secure browsing, endpoint security.",
        "q3_competency_alignment": "Critical finding: Categorized as 'Domain' in ACBP, but cyber hygiene is a core civil service digital literacy skill defined under KCM-FUNC-10 (Digital Fluency: Cybersecurity sub-theme).",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 30 minutes; introductory awareness checklist.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "CERT-In is the national nodal agency for responding to computer security incidents.",
        "counter_evidence_and_limitations": "Categorized as 'Domain' in ACBP, creating a potential false domain gap.",
        "alternative_kcm_candidates": "KCM-FUNC-10 (Digital Fluency)",
        "sme_adjudication_questions": "Given that basic cyber hygiene applies to all civil servants and is defined under KCM-FUNC-10 Digital Fluency, should this ACBP 'Domain' classification be reconciled to Functional?",
    },
    "BM-CASE-025": {
        "q1_course_identity": "ISTM Central Secretariat Manual of Office Procedure (CSMOP) provides authentic institutional curriculum; exact 90-minute course is unmirrored.",
        "q2_subject_coverage": "Secretariat noting, statutory referencing, drafting of cabinet notes/O.M.s, file docketing, disposal procedures.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-13 (Office Management) sub-theme on Noting and Drafting.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour 30 minutes. Focuses on supervisory critical noting and decision synthesis.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM is the statutory authority for Central Secretariat Office Procedure.",
        "counter_evidence_and_limitations": "Cadre-specific proficiency difference (SSO/SO vs clerical) must be evaluated.",
        "alternative_kcm_candidates": "KCM-FUNC-13 (Office Management)",
        "sme_adjudication_questions": "For Section Officers / SSOs, does the syllabus assess intermediate/advanced noting (statutory rule interpretation, synthesizing conflicting branch views), and how is this differentiated from clerical staff?",
    },
    "BM-CASE-026": {
        "q1_course_identity": "ISTM CSMOP clerical handbook provides authentic institutional curriculum; exact 60-minute course is unmirrored.",
        "q2_subject_coverage": "Basic file movement, docketing, routine noting, communications of a routine nature (endorsements, acknowledgments).",
        "q3_competency_alignment": "Direct match to KCM-FUNC-13 (Office Management) sub-theme on Noting and Drafting at foundational operational level.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour. Targets routine secretariat drafting tasks.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM clerical training syllabus for UDC/LDC/MTS cadres.",
        "counter_evidence_and_limitations": "Duration is 1 hour; represents foundational operational proficiency.",
        "alternative_kcm_candidates": "KCM-FUNC-13 (Office Management)",
        "sme_adjudication_questions": "For clerical cadre, does the 1-hour session target foundational operational proficiency (docketing, routine acknowledgments), justifying a Level 1 proficiency tag?",
    },
}

# CSV column headers in deterministic order
CSV_HEADERS = [
    "benchmark_case_id",
    "stratum",
    "course_record_id",
    "course_name",
    "cadre_role",
    "acbp_competency_category",
    "duration",
    "course_creator",
    "current_evidence_status",
    "evidence_source_id",
    "evidence_source_title",
    "evidence_institution",
    "evidence_url_or_path",
    "evidence_publication_year",
    "evidence_type",
    "match_fidelity",
    "evidence_excerpt_verbatim",
    "is_exact_course_evidence",
    "missing_evidence_details",
    "candidate_kcm_id",
    "candidate_kcm_name",
    "candidate_kcm_type",
    "kcm_source_citation",
    "kcm_verbatim_definition",
    "kcm_verbatim_subthemes",
    "question_1_course_identity_finding",
    "question_2_subject_coverage_finding",
    "question_3_competency_alignment_finding",
    "question_4_evidence_sufficiency_finding",
    "question_5_competency_depth_limitation",
    "triage_guidance_label",
    "evidence_supporting_proposed",
    "counter_evidence_and_limitations",
    "alternative_kcm_candidates",
    "sme_adjudication_questions",
    "adjudication_status",
    "adjudicated_label",
    "adjudicated_target_kcm_id",
    "adjudicated_target_kcm_name",
    "adjudicated_subtheme",
    "evidence_sufficiency_verdict",
    "depth_assessment",
    "reviewer_id",
    "reviewer_role",
    "adjudication_date",
    "reviewer_rationale",
    "confidence_rating",
    "second_reviewer_required",
    "consensus_status",
]


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_input_datasets() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    # Verify immutable baselines
    course_hash = compute_sha256(COURSES_JSON_PATH)
    if course_hash != EXPECTED_COURSE_HASH:
        raise ValueError(f"acbp_courses.json hash mismatch: {course_hash}")

    kcm_hash = compute_sha256(KCM_JSON_PATH)
    if kcm_hash != EXPECTED_KCM_HASH:
        raise ValueError(f"competencies_kcm.json hash mismatch: {kcm_hash}")

    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    with open(LEDGER_JSON_PATH, "r", encoding="utf-8") as f:
        ledger_data = json.load(f)

    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        audit_data = json.load(f)

    with open(COURSES_JSON_PATH, "r", encoding="utf-8") as f:
        courses_raw = json.load(f)["records"]
        courses_dict = {c["record_id"]: c for c in courses_raw}

    with open(KCM_JSON_PATH, "r", encoding="utf-8") as f:
        kcm_raw = json.load(f)
        kcm_dict = {k["competency_id"]: k for k in kcm_raw}

    with open(EVIDENCE_PACK_JSON_PATH, "r", encoding="utf-8") as f:
        pack_raw = json.load(f)["evidence_pack"]
        pack_dict = {p["benchmark_case_id"]: p for p in pack_raw}

    return manifest_data, ledger_data, audit_data, courses_dict, kcm_dict, pack_dict


def build_adjudication_cases() -> List[Dict[str, Any]]:
    manifest_data, ledger_data, audit_data, courses_dict, kcm_dict, pack_dict = load_input_datasets()

    ledger_by_id = {r["benchmark_case_id"]: r for r in ledger_data["records"]}
    audit_by_id = {c["benchmark_case_id"]: c for c in audit_data["cases"]}

    adjudication_cases: List[Dict[str, Any]] = []

    for manifest_case in manifest_data["cases"]:
        case_id = manifest_case["benchmark_case_id"]
        course_id = manifest_case["course_record_id"]
        course = courses_dict[course_id]
        ledger_rec = ledger_by_id[case_id]
        audit_rec = audit_by_id[case_id]
        pack_rec = pack_dict[case_id]
        spec = CASE_ADJUDICATION_SPECS[case_id]

        # Determine KCM candidate information
        candidate_kcm_id = manifest_case.get("candidate_kcm_competency_id")
        candidate_kcm_name = manifest_case.get("candidate_kcm_competency_name")
        candidate_kcm_type = manifest_case.get("candidate_kcm_competency_type")

        # If not in manifest, check if audit identified an institutional claimed candidate
        if candidate_kcm_id is None and audit_rec.get("claimed_kcm_id"):
            candidate_kcm_id = audit_rec["claimed_kcm_id"]
            candidate_kcm_name = audit_rec["claimed_kcm_name"]
            if candidate_kcm_id in kcm_dict:
                candidate_kcm_type = kcm_dict[candidate_kcm_id]["competency_type"]

        # Extract KCM definition and subthemes if candidate exists
        kcm_source_citation: Optional[str] = None
        kcm_definition: Optional[str] = None
        kcm_subthemes: Optional[str] = None

        if candidate_kcm_id and candidate_kcm_id in kcm_dict:
            kcm_entry = kcm_dict[candidate_kcm_id]
            kcm_source_citation = f"{kcm_entry['source_id']} (Page {kcm_entry['source_page']})"
            kcm_definition = kcm_entry["description"]
            behaviours = kcm_entry.get("behaviours", [])
            kcm_subthemes = " | ".join(behaviours) if behaviours else None

        # Build adjudication card
        case_record: Dict[str, Any] = {
            # 1. Identifiers & Course Metadata
            "benchmark_case_id": case_id,
            "stratum": manifest_case["stratum"],
            "course_record_id": course_id,
            "course_name": course["course_name"],
            "cadre_role": course["cadre_role"],
            "acbp_competency_category": course["competency_category"],
            "duration": course["duration"],
            "course_creator": course["course_creator"],
            # 2. Evidence Provenance & Audit Classification
            "current_evidence_status": audit_rec["audit_classification"],
            "evidence_source_id": "SRC-CBC-IGOT-2024" if audit_rec["audit_classification"] == "access_restricted" else "SRC-OFFICIAL-ACADEMY-2024",
            "evidence_source_title": ledger_rec["source_document_title"],
            "evidence_institution": ledger_rec["source_institution"],
            "evidence_url_or_path": ledger_rec["source_url_or_path"],
            "evidence_publication_year": ledger_rec["evidence_publication_year"],
            "evidence_type": ledger_rec["evidence_type"],
            "match_fidelity": ledger_rec["match_fidelity"],
            "evidence_excerpt_verbatim": ledger_rec["evidence_excerpt_verbatim"],
            "is_exact_course_evidence": False,  # Established in Stage 3.4.1: no local exact course session plans
            "missing_evidence_details": ledger_rec["missing_evidence_details"],
            # 3. KCM Candidate Reference
            "candidate_kcm_id": candidate_kcm_id,
            "candidate_kcm_name": candidate_kcm_name,
            "candidate_kcm_type": candidate_kcm_type,
            "kcm_source_citation": kcm_source_citation,
            "kcm_verbatim_definition": kcm_definition,
            "kcm_verbatim_subthemes": kcm_subthemes,
            # 4. Six-Question Adjudication Guidance
            "question_1_course_identity_finding": spec["q1_course_identity"],
            "question_2_subject_coverage_finding": spec["q2_subject_coverage"],
            "question_3_competency_alignment_finding": spec["q3_competency_alignment"],
            "question_4_evidence_sufficiency_finding": spec["q4_evidence_sufficiency"],
            "question_5_competency_depth_limitation": spec["q5_competency_depth"],
            "triage_guidance_label": spec["triage_guidance_label"],
            "evidence_supporting_proposed": spec["evidence_supporting_proposed"],
            "counter_evidence_and_limitations": spec["counter_evidence_and_limitations"],
            "alternative_kcm_candidates": spec["alternative_kcm_candidates"],
            "sme_adjudication_questions": spec["sme_adjudication_questions"],
            # 5. Blank Human Adjudication Fields (Strictly null for human review)
            "adjudication_status": "pending_review",
            "adjudicated_label": None,
            "adjudicated_target_kcm_id": None,
            "adjudicated_target_kcm_name": None,
            "adjudicated_subtheme": None,
            "evidence_sufficiency_verdict": None,
            "depth_assessment": None,
            "reviewer_id": None,
            "reviewer_role": None,
            "adjudication_date": None,
            "reviewer_rationale": None,
            "confidence_rating": None,
            "second_reviewer_required": None,
            "consensus_status": None,
        }

        adjudication_cases.append(case_record)

    return adjudication_cases


def export_adjudication_packet(cases: List[Dict[str, Any]]) -> None:
    # Summary calculations
    strata_counts: Dict[str, int] = {}
    evidence_status_counts: Dict[str, int] = {}

    for c in cases:
        st = c["stratum"]
        strata_counts[st] = strata_counts.get(st, 0) + 1

        ev = c["current_evidence_status"]
        evidence_status_counts[ev] = evidence_status_counts.get(ev, 0) + 1

    packet_json_content: Dict[str, Any] = {
        "packet_id": "ADJ-PACKET-BM-PILOT-MOSPI-2026-V1",
        "benchmark_id": "BM-PILOT-MOSPI-2026-V1",
        "version": "1.0.0",
        "stage": "3.4.2",
        "created_at": "2026-10-18T16:00:00Z",
        "total_cases": len(cases),
        "strata_summary": strata_counts,
        "evidence_status_summary": evidence_status_counts,
        "adjudication_status_summary": {
            "pending_review": len(cases),
            "review_in_progress": 0,
            "adjudicated": 0,
            "requires_more_evidence": 0,
        },
        "allowed_benchmark_labels": [
            "supported_mapping",
            "plausible_insufficient_evidence",
            "incorrect_mapping",
            "unresolved_insufficient_source",
            "no_applicable_kcm_competency",
        ],
        "allowed_evidence_sufficiency": [
            "sufficient",
            "insufficient",
            "absent",
        ],
        "allowed_adjudication_statuses": [
            "pending_review",
            "review_in_progress",
            "adjudicated",
            "requires_more_evidence",
        ],
        "confidence_rating_scale": {
            "1": "Very Low: Speculative or title-only evidence; no verifiable syllabus or session plan.",
            "2": "Low: Related subject material identified, but exact iGOT course module outline is unverified.",
            "3": "Moderate: Apex institutional curriculum verified, but course duration or delivery modality differs from online micro-course.",
            "4": "High: Granular course session outline verified with direct alignment to specific KCM sub-theme indicators.",
            "5": "Very High: Complete syllabus with observable behavioral learning outcomes and assessment criteria verified.",
        },
        "consensus_workflow_rules": {
            "single_reviewer_threshold": "Allowed only when confidence >= 4 and supported by Level 3/4 syllabus evidence.",
            "dual_reviewer_mandatory": "Mandatory for all cases with confidence <= 3, all Domain gap cases, and all title-reference candidates.",
            "disagreement_escalation": "When two independent reviewers assign different benchmark labels, case is escalated to an NSSTA / MoSPI subject-matter expert panel.",
        },
        "cases": cases,
    }

    # Write JSON
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    with open(PACKET_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(packet_json_content, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Exported JSON adjudication packet: {PACKET_JSON_PATH} ({len(cases)} cases)")

    # Write CSV
    with open(PACKET_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for c in cases:
            row = []
            for h in CSV_HEADERS:
                val = c.get(h)
                if val is None:
                    row.append("")
                elif isinstance(val, bool):
                    row.append("true" if val else "false")
                else:
                    row.append(str(val))
            writer.writerow(row)
    print(f"[SUCCESS] Exported CSV adjudication packet: {PACKET_CSV_PATH} ({len(cases)} rows)")


def main() -> None:
    print("=" * 70)
    print("MoSPI SIH26101: Building Human Adjudication Packet (Stage 3.4.2)")
    print("=" * 70)
    cases = build_adjudication_cases()
    export_adjudication_packet(cases)
    print("=" * 70)
    print("Adjudication packet compilation completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
