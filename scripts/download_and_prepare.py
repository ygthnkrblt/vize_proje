#!/usr/bin/env python3
"""Download OASST1 and create privacy-minimized CSVs for the Kura 8 project.

Only Python's standard library is required. The original compressed JSONL is
kept unchanged under data/raw/. Processed files omit message text and user_id.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import random
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SOURCE_URL = (
    "https://huggingface.co/datasets/OpenAssistant/oasst1/resolve/main/"
    "2023-04-12_oasst_ready.messages.jsonl.gz"
)
SOURCE_FILENAME = "2023-04-12_oasst_ready.messages.jsonl.gz"
EXPECTED_SHA256 = "286a6e9a5a413b3272ae9c0b5a20d327983dea1c24342ae28cb244a6da65185c"
EVENT_THRESHOLD = 0.20
SCORE_FIELDS = (
    "toxicity",
    "severe_toxicity",
    "obscene",
    "identity_attack",
    "insult",
    "threat",
    "sexual_explicit",
)


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def score_value(detoxify: Any, key: str) -> float | None:
    if not isinstance(detoxify, dict):
        return None
    value = detoxify.get(key)
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not 0.0 <= number <= 1.0:
        return None
    return number


def classify_conversation(root_text: str | None) -> str:
    """Rule-based topic label; this is not a human-assigned dataset label."""
    text = (root_text or "").lower()
    if re.search(r"\b(grammar|tense|verb|adjective|sentence structure|punctuation|syntax)\b", text):
        return "grammar_practice"
    if re.search(r"\b(vocabulary|synonym|antonym|word meaning|define|definition|idiom)\b", text):
        return "vocabulary"
    if re.search(r"\b(translate|translation|translate this|how do you say)\b", text):
        return "translation"
    if re.search(r"\b(essay|paragraph|proofread|writing|correct my|rewrite my|writing feedback)\b", text):
        return "writing_help"
    return "other_or_general"


def make_type_variant(value: str, index: int) -> str:
    """Create controlled formatting variants for the cleaning demonstration.

    These are derived labels, not altered source fields or generated conversations.
    """
    if index % 13 == 0:
        return value.upper()
    if index % 11 == 0:
        return f" {value} "
    if index % 7 == 0:
        return value.title()
    return value


def severity_from_score(score: float) -> int:
    if score < 0.35:
        return 1
    if score < 0.50:
        return 2
    if score < 0.65:
        return 3
    if score < 0.80:
        return 4
    return 5


def download_file(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Kura8-Student-Project/1.0"},
    )
    print(f"Kaynak indiriliyor: {SOURCE_URL}")
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temp_path.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        actual_hash = sha256_file(temp_path)
        if actual_hash.lower() != EXPECTED_SHA256:
            raise RuntimeError(
                "İndirilen dosyanın SHA-256 değeri beklenen değerle eşleşmedi. "
                f"Beklenen={EXPECTED_SHA256}, gelen={actual_hash}. Dosya kullanılmadı."
            )
        temp_path.replace(destination)
        print(f"İndirme ve SHA-256 doğrulaması başarılı: {destination}")
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_groups(source_path: Path) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    accepted = 0
    skipped_invalid = 0
    with gzip.open(source_path, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                skipped_invalid += 1
                continue
            if row.get("lang") != "en":
                continue
            if row.get("tree_state") != "ready_for_export":
                continue
            if row.get("deleted") is True:
                continue
            tree_id = row.get("message_tree_id") or row.get("message_id")
            if not tree_id:
                continue
            groups[str(tree_id)].append(row)
            accepted += 1
    print(f"İngilizce ve hazır durumdaki kaynak mesajı: {accepted:,}")
    if skipped_invalid:
        print(f"Bozuk JSON satırı atlandı: {skipped_invalid}")
    return groups


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def fmt_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def build_dataset(source_path: Path, output_dir: Path, limit: int, min_conversations: int) -> None:
    groups = read_groups(source_path)

    eligible: list[tuple[str, list[dict[str, Any]], datetime | None]] = []
    for tree_id, rows in groups.items():
        if len(rows) < 2:
            continue
        if not any(row.get("role") == "prompter" for row in rows):
            continue
        dates = [parse_datetime(row.get("created_date")) for row in rows]
        valid_dates = [date for date in dates if date is not None]
        started_at = min(valid_dates) if valid_dates else None
        eligible.append((tree_id, rows, started_at))

    # Fixed seed makes the sample reproducible while avoiding a purely chronological slice.
    rng = random.Random(105)
    rng.shuffle(eligible)
    selected = eligible[:limit]
    if len(selected) < min_conversations:
        raise RuntimeError(
            f"Yalnızca {len(selected)} uygun İngilizce konuşma bulundu; gereken en az "
            f"{min_conversations}. Veri setinin hazır dışa aktarma sürümünü kontrol et. "
            "500 altındaki örnek teslim için kullanılmamalıdır."
        )

    conversation_rows: list[dict[str, Any]] = []
    stage_rows: list[dict[str, Any]] = []
    message_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    category_index = 0

    for tree_id, tree_messages, started_at in selected:
        sorted_messages = sorted(
            tree_messages,
            key=lambda row: (
                parse_datetime(row.get("created_date")) or datetime.max.replace(tzinfo=timezone.utc),
                str(row.get("message_id") or ""),
            ),
        )
        root_candidates = [row for row in sorted_messages if row.get("parent_id") is None and row.get("role") == "prompter"]
        if not root_candidates:
            root_candidates = [row for row in sorted_messages if row.get("role") == "prompter"]
        root_text = (root_candidates[0].get("text") if root_candidates else None)
        clean_type = classify_conversation(root_text)
        raw_type = make_type_variant(clean_type, category_index)
        category_index += 1

        tree_events: list[dict[str, Any]] = []
        for order, source_message in enumerate(sorted_messages, start=1):
            message_id = str(source_message.get("message_id") or f"{tree_id}-{order}")
            role = str(source_message.get("role") or "unknown").strip().lower()
            sent_at = parse_datetime(source_message.get("created_date"))
            source_text = source_message.get("text")
            length_chars = len(source_text) if isinstance(source_text, str) and source_text.strip() else None
            detoxify = source_message.get("detoxify")
            scores = {key: score_value(detoxify, key) for key in SCORE_FIELDS}

            message_rows.append({
                "id": message_id,
                "conversation_id": tree_id,
                "sender": role,
                "message_order": order,
                "length_chars": length_chars,
                "sent_at": fmt_dt(sent_at),
                "toxicity_score": scores["toxicity"],
                "severe_toxicity_score": scores["severe_toxicity"],
                "obscene_score": scores["obscene"],
                "identity_attack_score": scores["identity_attack"],
                "insult_score": scores["insult"],
                "threat_score": scores["threat"],
                "sexual_explicit_score": scores["sexual_explicit"],
                "review_result": source_message.get("review_result"),
            })

            # Only assistant-generated messages are considered for assistant safety flags.
            if role == "assistant":
                available_scores = [(name, value) for name, value in scores.items() if value is not None]
                if available_scores:
                    event_type, risk_score = max(available_scores, key=lambda item: item[1])
                    if risk_score >= EVENT_THRESHOLD:
                        tree_events.append({
                            "id": f"{message_id}-flag",
                            "conversation_id": tree_id,
                            "message_id": message_id,
                            "event_type": event_type,
                            "severity_1_5": severity_from_score(risk_score),
                            "message_order": order,
                            "detected_at": fmt_dt(sent_at),
                            "risk_score": round(risk_score, 6),
                            "detection_source": "detoxify_score_proxy",
                        })

        event_rows.extend(tree_events)
        conversation_rows.append({
            "id": tree_id,
            "conversation_type": raw_type.strip().lower(),
            "started_at": fmt_dt(started_at),
            "message_count": len(sorted_messages),
            "event_count": len(tree_events),
            "source_language": "en",
        })
        stage_rows.append({
            "id": tree_id,
            "conversation_type_raw": raw_type,
            "started_at": fmt_dt(started_at),
            "message_count": len(sorted_messages),
            "event_count": len(tree_events),
            "source_language": "en",
        })

    # Stable sort makes CSV order easier to inspect and compare between runs.
    conversation_rows.sort(key=lambda row: (row["started_at"] or "", row["id"]))
    stage_rows.sort(key=lambda row: (row["started_at"] or "", row["id"]))
    message_rows.sort(key=lambda row: (row["sent_at"] or "", row["conversation_id"], row["message_order"]))
    event_rows.sort(key=lambda row: (row["detected_at"] or "", row["conversation_id"], row["message_order"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    conversation_fields = ["id", "conversation_type", "started_at", "message_count", "event_count", "source_language"]
    stage_fields = ["id", "conversation_type_raw", "started_at", "message_count", "event_count", "source_language"]
    message_fields = [
        "id", "conversation_id", "sender", "message_order", "length_chars", "sent_at",
        "toxicity_score", "severe_toxicity_score", "obscene_score", "identity_attack_score",
        "insult_score", "threat_score", "sexual_explicit_score", "review_result",
    ]
    event_fields = [
        "id", "conversation_id", "message_id", "event_type", "severity_1_5",
        "message_order", "detected_at", "risk_score", "detection_source",
    ]

    n_conversations = write_csv(output_dir / "conversations.csv", conversation_fields, conversation_rows)
    n_stage = write_csv(output_dir / "conversations_stage.csv", stage_fields, stage_rows)
    n_messages = write_csv(output_dir / "messages.csv", message_fields, message_rows)
    n_events = write_csv(output_dir / "events.csv", event_fields, event_rows)

    date_values = [row["started_at"] for row in conversation_rows if row["started_at"]]
    event_types: dict[str, int] = defaultdict(int)
    for row in event_rows:
        event_types[row["event_type"]] += 1
    null_lengths = sum(1 for row in message_rows if row["length_chars"] in (None, ""))
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    summary = {
        "generated_at": generated_at,
        "source_file": SOURCE_FILENAME if source_path.name == SOURCE_FILENAME else source_path.name,
        "source_sha256": sha256_file(source_path),
        "source_url": SOURCE_URL,
        "license": "Apache-2.0",
        "selected_conversations": n_conversations,
        "staging_conversations": n_stage,
        "messages": n_messages,
        "events": n_events,
        "null_length_chars": null_lengths,
        "date_min": min(date_values) if date_values else None,
        "date_max": max(date_values) if date_values else None,
        "event_threshold": EVENT_THRESHOLD,
        "event_types": dict(sorted(event_types.items())),
        "generated_conversation_rows": 0,
        "generated_message_rows": 0,
        "derived_fields": ["conversation_type", "message_order", "length_chars", "event_type", "severity_1_5", "event_count"],
    }
    (output_dir / "build_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    card_lines = [
        "# Veri Kartı — Çalıştırma Özeti",
        "",
        f"- Oluşturulma zamanı: {generated_at}",
        f"- Kaynak dosya: `{summary['source_file']}`",
        f"- SHA-256: `{summary['source_sha256']}`",
        f"- Lisans: {summary['license']}",
        f"- Konuşma satırı: {n_conversations:,}",
        f"- Staging konuşma satırı: {n_stage:,}",
        f"- Mesaj satırı: {n_messages:,}",
        f"- Olay/inceleme işareti satırı: {n_events:,}",
        f"- NULL length_chars: {null_lengths:,}",
        f"- Başlangıç tarih aralığı: {summary['date_min']} — {summary['date_max']}",
        f"- Olay eşiği: {EVENT_THRESHOLD}",
        f"- Üretilmiş konuşma/mesaj satırı: 0 / 0",
        "",
        "## Olay türü dağılımı",
        "",
    ]
    if event_types:
        card_lines.extend([f"- `{key}`: {value:,}" for key, value in sorted(event_types.items())])
    else:
        card_lines.append("- Seçilen örnekte eşik üstü asistan mesajı bulunmadı.")
    card_lines.extend([
        "",
        "> Not: Olay satırları Detoxify puanlarından türetilen tarama işaretleridir; doğrulanmış ihlal değildir. Kaynak metin ve user_id işlenmiş CSV'lere aktarılmaz.",
        "",
    ])
    (output_dir / "data_card_run.md").write_text("\n".join(card_lines), encoding="utf-8")

    print("\nİşleme tamamlandı:")
    print(f"  Konuşma: {n_conversations:,}")
    print(f"  Mesaj:   {n_messages:,}")
    print(f"  Olay:    {n_events:,}")
    print(f"  NULL uzunluk: {null_lengths:,}")
    print(f"  Çıktı:   {output_dir.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="OASST1 indir ve Kura 8 CSV dosyalarını üret.")
    parser.add_argument("--limit-conversations", type=int, default=800, help="Seçilecek konuşma sayısı (varsayılan: 800).")
    parser.add_argument("--min-conversations", type=int, default=500, help="Asgari kabul edilen konuşma sayısı (varsayılan: 500).")
    parser.add_argument("--source-file", type=Path, default=None, help="Test veya mevcut dosya için yerel .jsonl.gz yolu.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"), help="CSV çıktılarının dizini.")
    args = parser.parse_args()

    if args.limit_conversations < args.min_conversations:
        parser.error("--limit-conversations, --min-conversations değerinden küçük olamaz.")

    project_root = Path(__file__).resolve().parents[1]
    source_path = args.source_file or (project_root / "data" / "raw" / SOURCE_FILENAME)
    output_dir = args.output_dir if args.output_dir.is_absolute() else project_root / args.output_dir

    try:
        if not source_path.exists():
            if args.source_file:
                raise FileNotFoundError(f"Yerel kaynak dosyası bulunamadı: {source_path}")
            download_file(source_path)
        if source_path.stat().st_size == 0:
            raise RuntimeError("Kaynak dosya boş.")
        if not args.source_file:
            actual_hash = sha256_file(source_path)
            if actual_hash.lower() != EXPECTED_SHA256:
                raise RuntimeError(
                    "data/raw içindeki kaynak dosyanın SHA-256 değeri uyuşmuyor. "
                    "Dosyayı silip betiği yeniden çalıştır: "
                    f"beklenen={EXPECTED_SHA256}, gelen={actual_hash}"
                )
        build_dataset(source_path, output_dir, args.limit_conversations, args.min_conversations)
        return 0
    except (OSError, RuntimeError, urllib.error.URLError, gzip.BadGzipFile) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
