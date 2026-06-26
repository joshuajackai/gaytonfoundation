#!/usr/bin/env python3
"""
Organize Zoom Cloud transcripts and email them.

Flow:
  1. Authenticate to Zoom (Server-to-Server OAuth) and list recent cloud recordings.
  2. For each recording that has a VTT transcript we have not processed yet,
     download the transcript and turn it into a clean, readable document.
  3. Optionally use the Claude API to produce a summary + action items by person.
  4. Email the organized result via the Gmail API.
  5. Record processed transcripts in a state file so they are never re-sent.

Everything is done over plain HTTPS with the `requests` library so the only
dependency is `requests`. Configuration comes entirely from environment
variables (wired up as GitHub Actions secrets) -- see automation/README.md.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import os
import re
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import requests

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

ZOOM_ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID", "")
ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID", "")
ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET", "")
# Which Zoom user's recordings to scan. "me" works for the account owner;
# otherwise set to the user's email / userId.
ZOOM_USER_ID = os.environ.get("ZOOM_USER_ID", "me")

GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN", "")
# The mailbox the refresh token belongs to (used as the "From" address).
GMAIL_SENDER = os.environ.get("GMAIL_SENDER", "me")

# Where organized transcripts get emailed.
RECIPIENT = os.environ.get("TRANSCRIPT_RECIPIENT", "joshua@demanddesigner.com")

# Optional: enables AI summary + action-items-by-person. Without it you still
# get a cleanly formatted transcript.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# How many days back to scan for new recordings on each run.
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7"))

STATE_FILE = os.environ.get("STATE_FILE", ".github/zoom-transcript-state.json")

REQUEST_TIMEOUT = 60


# --------------------------------------------------------------------------- #
# State helpers
# --------------------------------------------------------------------------- #

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"processed": []}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")


# --------------------------------------------------------------------------- #
# Zoom API
# --------------------------------------------------------------------------- #

def zoom_access_token() -> str:
    """Get a Server-to-Server OAuth access token."""
    resp = requests.post(
        "https://zoom.us/oauth/token",
        params={"grant_type": "account_credentials", "account_id": ZOOM_ACCOUNT_ID},
        auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def list_recordings(token: str) -> list[dict]:
    """List cloud recordings for the configured user within the lookback window."""
    today = dt.datetime.utcnow().date()
    start = today - dt.timedelta(days=LOOKBACK_DAYS)
    headers = {"Authorization": f"Bearer {token}"}

    meetings: list[dict] = []
    next_page_token = ""
    while True:
        params = {
            "from": start.isoformat(),
            "to": today.isoformat(),
            "page_size": 300,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token
        resp = requests.get(
            f"https://api.zoom.us/v2/users/{ZOOM_USER_ID}/recordings",
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        meetings.extend(data.get("meetings", []))
        next_page_token = data.get("next_page_token", "")
        if not next_page_token:
            break
    return meetings


def find_transcript_file(meeting: dict) -> dict | None:
    """Return the VTT transcript recording-file entry, if present and completed."""
    for f in meeting.get("recording_files", []):
        if f.get("file_type") == "TRANSCRIPT" and f.get("status", "completed") == "completed":
            return f
    return None


def download_transcript(token: str, download_url: str) -> str:
    resp = requests.get(
        download_url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.text


# --------------------------------------------------------------------------- #
# VTT parsing / cleanup
# --------------------------------------------------------------------------- #

_TS_LINE = re.compile(r"-->")
_CUE_INDEX = re.compile(r"^\d+$")
_TS_GRAB = re.compile(r"(\d{2}:\d{2}:\d{2})")


def parse_vtt(vtt: str) -> list[dict]:
    """Parse a WEBVTT transcript into a list of {start, speaker, text} cues."""
    cues: list[dict] = []
    lines = vtt.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line == "WEBVTT" or _CUE_INDEX.match(line):
            i += 1
            continue
        if _TS_LINE.search(line):
            ts_match = _TS_GRAB.search(line)
            start = ts_match.group(1) if ts_match else ""
            i += 1
            text_parts = []
            while i < len(lines) and lines[i].strip() and not _TS_LINE.search(lines[i]):
                text_parts.append(lines[i].strip())
                i += 1
            text = " ".join(text_parts).strip()
            speaker = ""
            # Zoom encodes the speaker as "Name: utterance".
            if ":" in text:
                maybe_speaker, rest = text.split(":", 1)
                if len(maybe_speaker) <= 60 and "://" not in maybe_speaker:
                    speaker = maybe_speaker.strip()
                    text = rest.strip()
            if text:
                cues.append({"start": start, "speaker": speaker, "text": text})
        else:
            i += 1
    return cues


def group_by_speaker(cues: list[dict]) -> list[dict]:
    """Merge consecutive cues from the same speaker into single blocks."""
    blocks: list[dict] = []
    for cue in cues:
        if blocks and blocks[-1]["speaker"] == cue["speaker"]:
            blocks[-1]["text"] += " " + cue["text"]
        else:
            blocks.append({"start": cue["start"], "speaker": cue["speaker"], "text": cue["text"]})
    return blocks


def transcript_to_markdown(blocks: list[dict]) -> str:
    out = []
    for b in blocks:
        ts = f"`{b['start']}` " if b["start"] else ""
        speaker = f"**{b['speaker']}:** " if b["speaker"] else ""
        out.append(f"{ts}{speaker}{b['text']}")
    return "\n\n".join(out)


def participants(blocks: list[dict]) -> list[str]:
    seen = []
    for b in blocks:
        if b["speaker"] and b["speaker"] not in seen:
            seen.append(b["speaker"])
    return seen


# --------------------------------------------------------------------------- #
# Optional AI summary
# --------------------------------------------------------------------------- #

def ai_summary(transcript_md: str) -> str | None:
    """Use the Claude API to produce a summary + action items grouped by person."""
    if not ANTHROPIC_API_KEY:
        return None
    prompt = (
        "You are organizing a meeting transcript. Produce concise, well-structured "
        "Markdown with exactly these sections:\n\n"
        "## Summary\nA short paragraph of what the meeting covered.\n\n"
        "## Key Decisions\nBullet points of decisions made.\n\n"
        "## Action Items by Person\nGroup to-dos under each responsible person as a "
        "bulleted checklist. If a timestamp is available include it in parentheses.\n\n"
        "Only output the Markdown, no preamble.\n\n"
        "Transcript:\n\n" + transcript_md[:180000]
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": ANTHROPIC_MODEL,
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        parts = resp.json().get("content", [])
        text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
        return text.strip() or None
    except requests.RequestException as exc:
        print(f"  ! AI summary failed, continuing without it: {exc}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------- #
# Rendering + Gmail
# --------------------------------------------------------------------------- #

def md_to_basic_html(md: str) -> str:
    """Tiny Markdown-ish to HTML converter (headings, bold, bullets, paragraphs)."""
    html_lines = []
    in_list = False
    for raw in md.splitlines():
        line = raw.rstrip()
        line_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line_html = re.sub(r"`(.+?)`", r"<code>\1</code>", line_html)
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{line_html[3:]}</h2>")
        elif line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{line_html[2:]}</h1>")
        elif line.lstrip().startswith(("- ", "* ")):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = line_html.lstrip()[2:]
            item = re.sub(r"^\[[ xX]\]\s*", "", item)
            html_lines.append(f"<li>{item}</li>")
        elif not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{line_html}</p>")
    if in_list:
        html_lines.append("</ul>")
    body = "\n".join(html_lines)
    return (
        "<html><body style=\"font-family:-apple-system,Segoe UI,Roboto,Helvetica,"
        "Arial,sans-serif;line-height:1.5;color:#1a1a1a;max-width:760px;margin:auto\">"
        f"{body}</body></html>"
    )


def gmail_access_token() -> str:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GMAIL_CLIENT_ID,
            "client_secret": GMAIL_CLIENT_SECRET,
            "refresh_token": GMAIL_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def send_email(token: str, subject: str, markdown_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Zoom Transcript Bot", GMAIL_SENDER if GMAIL_SENDER != "me" else RECIPIENT))
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(markdown_body, "plain", "utf-8"))
    msg.attach(MIMEText(md_to_basic_html(markdown_body), "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    resp = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"raw": raw},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def build_document(meeting: dict, blocks: list[dict]) -> tuple[str, str]:
    topic = meeting.get("topic", "Zoom Meeting")
    start_time = meeting.get("start_time", "")[:16].replace("T", " ")
    people = participants(blocks)
    transcript_md = transcript_to_markdown(blocks)

    header = [f"# {topic}"]
    if start_time:
        header.append(f"**Date (UTC):** {start_time}")
    if people:
        header.append(f"**Participants:** {', '.join(people)}")
    header.append("")

    summary = ai_summary(transcript_md)
    sections = ["\n".join(header)]
    if summary:
        sections.append(summary)
    sections.append("## Full Transcript\n\n" + transcript_md)

    subject = f"[Transcript] {topic} — {start_time}".strip(" —")
    return subject, "\n\n".join(sections)


def main() -> int:
    missing = [
        name
        for name, val in {
            "ZOOM_ACCOUNT_ID": ZOOM_ACCOUNT_ID,
            "ZOOM_CLIENT_ID": ZOOM_CLIENT_ID,
            "ZOOM_CLIENT_SECRET": ZOOM_CLIENT_SECRET,
            "GMAIL_CLIENT_ID": GMAIL_CLIENT_ID,
            "GMAIL_CLIENT_SECRET": GMAIL_CLIENT_SECRET,
            "GMAIL_REFRESH_TOKEN": GMAIL_REFRESH_TOKEN,
        }.items()
        if not val
    ]
    if missing:
        print(f"ERROR: missing required secrets: {', '.join(missing)}", file=sys.stderr)
        return 1

    state = load_state()
    processed = set(state.get("processed", []))

    print(f"Scanning Zoom recordings for the last {LOOKBACK_DAYS} day(s)...")
    ztoken = zoom_access_token()
    meetings = list_recordings(ztoken)
    print(f"Found {len(meetings)} recording(s) in window.")

    new_count = 0
    gtoken = None
    for meeting in meetings:
        transcript_file = find_transcript_file(meeting)
        if not transcript_file:
            continue
        key = f"{meeting.get('uuid', '')}|{transcript_file.get('id', '')}"
        if key in processed:
            continue

        topic = meeting.get("topic", "Zoom Meeting")
        print(f"-> New transcript: {topic}")
        try:
            vtt = download_transcript(ztoken, transcript_file["download_url"])
            blocks = group_by_speaker(parse_vtt(vtt))
            if not blocks:
                print("   (empty transcript, skipping)")
                processed.add(key)
                continue
            subject, document = build_document(meeting, blocks)
            if gtoken is None:
                gtoken = gmail_access_token()
            send_email(gtoken, subject, document)
            print(f"   emailed to {RECIPIENT}")
            processed.add(key)
            new_count += 1
        except requests.RequestException as exc:
            print(f"   ! failed to process: {exc}", file=sys.stderr)
            # Do not mark processed so it retries next run.

    state["processed"] = sorted(processed)
    state["last_run_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    save_state(state)

    print(f"Done. {new_count} new transcript(s) emailed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
