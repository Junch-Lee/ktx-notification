import os
import requests
import korail2
from korail2 import Korail, AdultPassenger

# 1. 환경변수 로드
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
KORAIL_ID = os.environ.get("KORAIL_ID")
KORAIL_PW = os.environ.get("KORAIL_PW")

# 2. 조회 조건 설정 (본인에 맞게 수정)
DEP_STATION = "용산"       # 출발역
ARR_STATION = "목포"       # 도착역
DATE = "20260914"         # 출발일자 (YYYYMMDD)
TIME_START = "050000"     # 조회 시작 시간 (HHMMSS)
TIME_END = "180000"       # 조회 종료 시간 (HHMMSS)


def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def check_seats():
    try:
        # 코레일 로그인
        korail = Korail(KORAIL_ID, KORAIL_PW)
        
        # 열차 조회
        trains = korail.search_train(
            dep=DEP_STATION,
            arr=ARR_STATION,
            date=DATE,
            time=TIME_START,
            passengers=[AdultPassenger(1)],
            include_no_seats=True
        )

        available_trains = []
        for train in trains:
            # 설정한 시간 범위 내의 열차만 필터링
            train_time = train.dep_time
            if TIME_START <= train_time <= TIME_END:
                # 좌석 유무 확인 (예약 시도 없이 조회만 진행)
                if train.has_seat():
                    info = f"🚆 [{train.train_name}] {train.dep_name}({train.dep_time[:2]}:{train.dep_time[2:4]}) -> {train.arr_name}({train.arr_time[:2]}:{train.arr_time[2:4]}) - 잔여석 있음!"
                    available_trains.append(info)

        if available_trains:
            msg = "🔥 [KTX 취소표 발생 알림] 🔥\n\n" + "\n".join(available_trains) + "\n\n즉시 코레일톡 앱에서 예매하세요!"
            send_telegram_msg(msg)
            print("취소표 발견! 텔레그램 알림 발송 완료.")
        else:
            print("현재 예약 가능한 좌석이 없습니다.")

    except Exception as e:
        print(f"조회 중 오류 발생: {e}")

if __name__ == "__main__":
    check_seats()
