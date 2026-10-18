#!/usr/bin/env python3
"""
scripts/build_mapping_registry.py — Competency Mapping Registry & Review Queue Builder

Constructs the auditable Stage 3.2 mapping registry and human-review queue for all
226 MoSPI ACBP course allocations against the Karmayogi Competency Model (KCM).

Follows the schema and governance defined in:
- docs/competency_mapping_framework.md
- docs/competency_mapping_schema.md
- docs/competency_mapping_review.md
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

ACBP_COURSES_PATH = DATA_PROCESSED / "acbp_courses.json"
KCM_COMPETENCIES_PATH = DATA_PROCESSED / "competencies_kcm.json"
CANDIDATE_MAPPINGS_PATH = DATA_PROCESSED / "acbp_kcm_candidate_mappings.json"

MAPPINGS_JSON_PATH = DATA_PROCESSED / "acbp_kcm_mappings.json"
MAPPINGS_CSV_PATH = DATA_PROCESSED / "acbp_kcm_mappings.csv"
REVIEW_QUEUE_JSON_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.json"
REVIEW_QUEUE_CSV_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.csv"

PIPELINE_VERSION = "3.2.0"
FIXED_GENERATION_TIMESTAMP = "2026-10-18T14:40:00+00:00"

# Explicit KCM page mappings for known competencies (def_page, subtheme_page)
KCM_PAGE_LOOKUP: Dict[str, tuple[int, int]] = {
    "KCM-BEH-06": (49, 50),   # Collaboration
    "KCM-FUNC-05": (74, 75),  # Project Management
    "KCM-BEH-10": (57, 58),   # Strategic Leadership
}


def compute_sha256(path: Path) -> str:
    """Compute cryptographic SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_input_datasets() -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Load and index baseline input datasets without modifying them."""
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        course_data = json.load(f)
    courses = course_data.get("records", course_data) if isinstance(course_data, dict) else course_data

    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        kcm_list = json.load(f)
    kcm_by_id = {c["competency_id"]: c for c in kcm_list}

    with open(CANDIDATE_MAPPINGS_PATH, "r", encoding="utf-8") as f:
        cand_data = json.load(f)
    cand_by_course = {m["course_record_id"]: m for m in cand_data.get("mappings", [])}

    return courses, kcm_by_id, cand_by_course


def build_mapping_records(
    courses: List[Dict[str, Any]],
    kcm_by_id: Dict[str, Dict[str, Any]],
    cand_by_course: Dict[str, Dict[str, Any]],
    source_hash_course: str,
    source_hash_kcm: str,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build the 226 mapping records and corresponding review queue items."""
    mapping_records: List[Dict[str, Any]] = []
    review_queue: List[Dict[str, Any]] = []

    # Sequence counter for mapping IDs
    map_idx = 1

    for course in courses:
        cid = course["record_id"]
        c_title = course["course_name"]
        cadre = course["cadre_role"]
        category = course["competency_category"]
        page = course["source_page"]
        row = course["source_row"]

        mapping_id = f"MAP-ACBP-KCM-{map_idx:03d}"
        queue_id = f"REV-{map_idx:03d}"
        map_idx += 1

        cand = cand_by_course.get(cid)
        has_cand = cand is not None and cand.get("candidate_kcm_competency_id") is not None

        if has_cand:
            kcm_id = cand["candidate_kcm_competency_id"]
            kcm_rec = kcm_by_id.get(kcm_id, {})
            kcm_name = kcm_rec.get("competency_name", cand.get("candidate_kcm_competency_name"))
            kcm_type = kcm_rec.get("competency_type", cand.get("candidate_kcm_competency_type"))
            p_def, p_sub = KCM_PAGE_LOOKUP.get(kcm_id, (None, None))

            # Methodological correction from Stage 3.1 Review:
            # Reclassify from arbitrary heuristic float to exact_title_reference with null confidence
            mapping_type = "exact_title_reference"
            mapping_method = "verbatim_title_containment"
            evidence = (
                f"Course title contains verbatim token match for KCM competency '{kcm_name}'. "
                f"Curricular alignment across sub-themes and learning outcomes remains unverified "
                f"pending iGOT syllabus review."
            )
            val_status = "pending_review"

            queue_category = "title_reference_candidate"
            missing_evidence = (
                "Absence of modular course syllabus, lesson plan, and target proficiency depth. "
                "Requires confirmation that course content comprehensively addresses KCM sub-themes."
            )
            rec_action = (
                f"Audit course syllabus against KCM {kcm_id} sub-themes on Page {p_sub} to determine "
                "if candidate should be promoted to curated_candidate or rejected."
            )
            priority = "high"

            rec: Dict[str, Any] = {
                "mapping_id": mapping_id,
                "course_record_id": cid,
                "cadre_role": cadre,
                "course_name": c_title,
                "acbp_competency_category": category,
                "candidate_kcm_competency_id": kcm_id,
                "candidate_kcm_competency_name": kcm_name,
                "candidate_kcm_subtheme": None,
                "candidate_kcm_competency_type": kcm_type,
                "mapping_type": mapping_type,
                "mapping_method": mapping_method,
                "evidence_or_rationale": evidence,
                "course_source_id": "SRC-MOSPI-ACBP-2026-27",
                "course_source_page": page,
                "course_source_row": row,
                "kcm_source_id": "SRC-CBC-KCM-2024",
                "kcm_source_page_def": p_def,
                "kcm_source_page_sub": p_sub,
                "confidence_score": None,
                "confidence_metric": None,
                "validation_status": val_status,
                "reviewer_id": None,
                "reviewer_role": None,
                "reviewed_at": None,
                "reviewer_notes": "",
                "creation_method": "automated_pipeline",
                "pipeline_version": PIPELINE_VERSION,
                "created_at": FIXED_GENERATION_TIMESTAMP,
                "source_hash_course": source_hash_course,
                "source_hash_kcm": source_hash_kcm,
            }

        else:
            # Unresolved record
            kcm_id = None
            kcm_name = None
            kcm_type = None
            p_def = None
            p_sub = None
            mapping_type = "unresolved"
            val_status = "unresolved"

            if category == "Domain":
                mapping_method = "unresolved_domain_gap"
                evidence = (
                    "Official MoSPI Domain category course. The CBC KCM baseline defines zero "
                    "Domain competencies (Ministry-specific). Retained as unresolved pending "
                    "MoSPI/NSSTA Domain Competency Dictionary integration."
                )
                queue_category = "unresolved_domain_gap"
                missing_evidence = (
                    "MoSPI Official Statistics Domain Competency Dictionary absent from CBC KCM. "
                    "Do not force-map to generic functional competencies."
                )
                rec_action = (
                    "Await publication and integration of official MoSPI/NSSTA Domain Competency "
                    "Dictionary under Stage 4."
                )
                priority = "low"
            else:
                mapping_method = "unresolved_no_match"
                evidence = (
                    "No explicit title reference to KCM competencies in ACBP source text. "
                    "Curricular alignment requires modular iGOT course syllabi and learning outcome indicators."
                )
                queue_category = "unresolved_no_match"
                missing_evidence = (
                    "No textual match in course title. Absence of modular syllabus and learning outcomes "
                    "prevents defensible competency mapping."
                )
                rec_action = (
                    "Acquire iGOT modular curriculum outline to perform semantic and curricular comparison "
                    "in Stage 3.3+."
                )
                priority = "medium"

            rec = {
                "mapping_id": mapping_id,
                "course_record_id": cid,
                "cadre_role": cadre,
                "course_name": c_title,
                "acbp_competency_category": category,
                "candidate_kcm_competency_id": None,
                "candidate_kcm_competency_name": None,
                "candidate_kcm_subtheme": None,
                "candidate_kcm_competency_type": None,
                "mapping_type": mapping_type,
                "mapping_method": mapping_method,
                "evidence_or_rationale": evidence,
                "course_source_id": "SRC-MOSPI-ACBP-2026-27",
                "course_source_page": page,
                "course_source_row": row,
                "kcm_source_id": None,
                "kcm_source_page_def": None,
                "kcm_source_page_sub": None,
                "confidence_score": None,
                "confidence_metric": None,
                "validation_status": val_status,
                "reviewer_id": None,
                "reviewer_role": None,
                "reviewed_at": None,
                "reviewer_notes": "",
                "creation_method": "automated_pipeline",
                "pipeline_version": PIPELINE_VERSION,
                "created_at": FIXED_GENERATION_TIMESTAMP,
                "source_hash_course": source_hash_course,
                "source_hash_kcm": source_hash_kcm,
            }

        mapping_records.append(rec)

        # Build review queue entry
        q_entry = {
            "queue_id": queue_id,
            "mapping_id": mapping_id,
            "course_record_id": cid,
            "course_name": c_title,
            "cadre_role": cadre,
            "acbp_competency_category": category,
            "candidate_kcm_competency_id": kcm_id,
            "candidate_kcm_competency_name": kcm_name,
            "mapping_type": mapping_type,
            "validation_status": val_status,
            "queue_category": queue_category,
            "priority": priority,
            "evidence_or_rationale": evidence,
            "course_source_reference": f"SRC-MOSPI-ACBP-2026-27 (Page {page}, Row {row})",
            "kcm_source_reference": f"SRC-CBC-KCM-2024 ({kcm_id}, Pages [{p_def}, {p_sub}])" if kcm_id else None,
            "missing_evidence_or_ambiguity": missing_evidence,
            "recommended_action": rec_action,
        }
        review_queue.append(q_entry)

    return mapping_records, review_queue


def serialize_mappings_csv(records: List[Dict[str, Any]], output_path: Path) -> None:
    """Serialize mapping records to CSV with exact 1-to-1 parity."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records:
            # Format None as empty string
            row_dict = {k: ("" if v is None else v) for k, v in r.items()}
            writer.writerow(row_dict)


def serialize_review_queue_csv(records: List[Dict[str, Any]], output_path: Path) -> None:
    """Serialize review queue entries to CSV."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records:
            row_dict = {k: ("" if v is None else v) for k, v in r.items()}
            writer.writerow(row_dict)


def main() -> None:
    print("[1/5] Verifying baseline input datasets and recording hashes...")
    source_hash_kcm = compute_sha256(KCM_COMPETENCIES_PATH)
    source_hash_course = compute_sha256(ACBP_COURSES_PATH)
    source_hash_cand = compute_sha256(CANDIDATE_MAPPINGS_PATH)

    print(f"  - KCM Baseline SHA-256:       {source_hash_kcm}")
    print(f"  - ACBP Courses SHA-256:       {source_hash_course}")
    print(f"  - Candidate Mappings SHA-256: {source_hash_cand}")

    print("[2/5] Loading datasets...")
    courses, kcm_by_id, cand_by_course = load_input_datasets()
    print(f"  Loaded {len(courses)} ACBP courses, {len(kcm_by_id)} KCM competencies.")

    print("[3/5] Building mapping registry records and human-review queue...")
    mapping_records, review_queue = build_mapping_records(
        courses, kcm_by_id, cand_by_course, source_hash_course, source_hash_kcm
    )

    explicit_count = sum(1 for m in mapping_records if m["candidate_kcm_competency_id"] is not None)
    unresolved_count = sum(1 for m in mapping_records if m["candidate_kcm_competency_id"] is None)
    domain_gap_count = sum(1 for m in mapping_records if m["mapping_method"] == "unresolved_domain_gap")
    no_match_count = sum(1 for m in mapping_records if m["mapping_method"] == "unresolved_no_match")

    print(f"  - Total Courses Evaluated:  {len(mapping_records)}")
    print(f"  - Explicit Candidates:      {explicit_count} (all pending_review)")
    print(f"  - Total Unresolved Records: {unresolved_count}")
    print(f"    * Domain Gaps:            {domain_gap_count}")
    print(f"    * No Explicit Matches:    {no_match_count}")

    print("[4/5] Serializing mapping registry JSON & CSV...")
    registry_envelope = {
        "dataset_name": "MoSPI ACBP to Karmayogi Competency Model Mapping Registry",
        "course_source_id": "SRC-MOSPI-ACBP-2026-27",
        "kcm_source_id": "SRC-CBC-KCM-2024",
        "pipeline_version": PIPELINE_VERSION,
        "generation_timestamp": FIXED_GENERATION_TIMESTAMP,
        "total_courses_evaluated": len(mapping_records),
        "mapped_records_count": explicit_count,
        "unresolved_records_count": unresolved_count,
        "mappings": mapping_records,
    }
    with open(MAPPINGS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_envelope, f, indent=2, ensure_ascii=False)
    serialize_mappings_csv(mapping_records, MAPPINGS_CSV_PATH)
    print(f"  Saved {MAPPINGS_JSON_PATH.name} and {MAPPINGS_CSV_PATH.name}")

    print("[5/5] Serializing review queue JSON & CSV...")
    queue_envelope = {
        "dataset_name": "MoSPI ACBP to KCM Human Review Queue",
        "pipeline_version": PIPELINE_VERSION,
        "generation_timestamp": FIXED_GENERATION_TIMESTAMP,
        "total_queue_items": len(review_queue),
        "title_reference_candidates_count": explicit_count,
        "unresolved_domain_gaps_count": domain_gap_count,
        "unresolved_no_match_count": no_match_count,
        "queue": review_queue,
    }
    with open(REVIEW_QUEUE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(queue_envelope, f, indent=2, ensure_ascii=False)
    serialize_review_queue_csv(review_queue, REVIEW_QUEUE_CSV_PATH)
    print(f"  Saved {REVIEW_QUEUE_JSON_PATH.name} and {REVIEW_QUEUE_CSV_PATH.name}")
    print("\n[SUCCESS] Competency mapping registry and review queue generated deterministically.")


if __name__ == "__main__":
    main()
