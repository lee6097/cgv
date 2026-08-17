"""
CGV 용산아이파크몰 IMAX '오디세이' 예매 오픈 모니터링 스크립트

- CGV 공개 상영 스케줄 API(searchSchByMov)를 날짜별로 조회한다.
- 확인 대상 날짜: START_DATE ~ START_DATE + WATCH_DAYS
- 특정 날짜에 IMAX관 상영 스케줄이 처음 생기면(=예매 오픈) 이메일을 보낸다.
- 이미 알림을 보낸 날짜는 state.json에 기록해서 중복 발송을 막는다..
"""

import json
import os
import smtplib
import ssl
from datetime import date, timedelta
from email.mime.text import MIMEText
from pathlib import Path

import requests

# ── 설정 ──────────────────────────────────────────────────────────────
CO_CD = "A420"
SITE_NO = "0013"          # CGV 용산아이파크몰
MOV_NO = "30001323"       # 오디세이
TARGET_SCREEN_NM = "IMAX" # scnsNm에 이 문자열이 포함되면 IMAX 상영관으로 간주

START_DATE = date(2026, 8, 26)  # 이 날짜부터
WATCH_DAYS = 2                 # 오늘부터 2일치 날짜를 확인 (필요하면 조절)

STATE_FILE = Path(__file__).parent / "state.json"

API_URL = "https://cgv.co.kr/api/v1/booking/searchSchByMov"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://cgv.co.kr/",
}

# 이메일 설정은 환경변수로 받는다 (GitHub Actions Secrets에 등록)
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL", GMAIL_ADDRESS)


# ── 상태 저장/로드 ─────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"notified_dates": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── CGV API 조회 ───────────────────────────────────────────────────────
def check_date(ymd: str) -> bool:
    """해당 날짜(YYYYMMDD)에 용산 IMAX관 오디세이 상영 스케줄이 있으면 True."""
    params = {
        "coCd": CO_CD,
        "siteNo": SITE_NO,
        "scnYmd": ymd,
        "movNo": MOV_NO,
        "rtctlScopCd": "08",
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    if payload.get("statusCode") != 0:
        return False

    rows = payload.get("data") or []
    for row in rows:
        if row.get("siteNo") == SITE_NO and TARGET_SCREEN_NM in (row.get("scnsNm") or ""):
            return True
    return False


# ── 이메일 발송 ───────────────────────────────────────────────────────
def send_email(subject: str, body: str) -> None:
    if not (GMAIL_ADDRESS and GMAIL_APP_PASSWORD and TO_EMAIL):
        raise RuntimeError(
            "GMAIL_ADDRESS / GMAIL_APP_PASSWORD / TO_EMAIL 환경변수가 설정되지 않았습니다."
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [TO_EMAIL], msg.as_string())


# ── 메인 로직 ─────────────────────────────────────────────────────────
def main() -> None:
    state = load_state()
    notified = set(state.get("notified_dates", []))

    newly_opened = []

    for i in range(WATCH_DAYS):
        target_date = START_DATE + timedelta(days=i)
        ymd = target_date.strftime("%Y%m%d")

        if ymd in notified:
            continue  # 이미 알림 보낸 날짜는 스킵

        try:
            opened = check_date(ymd)
        except Exception as e:
            print(f"[{ymd}] 조회 실패: {e}")
            continue

        print(f"[{ymd}] IMAX 오디세이 오픈 여부: {opened}")

        if opened:
            newly_opened.append(target_date)
            notified.add(ymd)

    if newly_opened:
        date_list = ", ".join(d.strftime("%Y-%m-%d (%a)") for d in newly_opened)
        subject = f"[CGV 알림] 용산 IMAX 오디세이 예매 오픈! ({len(newly_opened)}일)"
        body = (
            f"용산아이파크몰 IMAX관 '오디세이' 예매가 새로 열렸습니다!\n\n"
            f"오픈된 날짜: {date_list}\n\n"
            f"바로 예매하세요: https://cgv.co.kr/\n"
        )
        send_email(subject, body)
        print("이메일 발송 완료:", date_list)
    else:
        print("새로 오픈된 날짜 없음.")

    state["notified_dates"] = sorted(notified)
    save_state(state)


if __name__ == "__main__":
    main()
