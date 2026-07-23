# Interpark Ticket Auto-Booking Bot

> ⚠️ **현재 이 프로젝트는 유지보수되지 않습니다.**
> 이어서 개발할 분은 아래 Known Issues를 참고하세요.

## Known Issues (2025 여름 기준, 미수정)

### 1. exe 실행 불가
Chrome 버전이 바뀔 때마다 ChromeDriver 버전 불일치 오류 발생. **exe 파일은 사용하지 말고 Python으로 직접 실행하세요.**

### 2. 야놀자 카카오 로그인 버튼 선택자 오류
야놀자가 로그인 페이지 HTML 구조를 변경함. 현재 코드의 CSS 선택자가 맞지 않아 카카오 로그인 버튼 클릭 후 새 탭이 열리지 않고 `TimeoutException` 발생.
`macro.py` 171번째 줄 근처 `div.KakaoLoginButton...` 선택자를 현재 야놀자 로그인 페이지 기준으로 업데이트 필요.

### 3. 캡챠 OCR 백엔드 (`fistol.thnos.app`) 미운영
캡챠 단계에서 OCR 백엔드 서버 호출 실패. 직접 백엔드를 배포하거나 `fistol-backend` 코드를 로컬에서 실행해야 함.

## 실행 방법 (Python 권장)

```bash
pip install undetected-chromedriver selenium selenium-stealth requests
python macro.py
```

---

This project is a **Python + Selenium automation script** for logging into **Yanolja & Interpark Ticket** and booking tickets automatically.  
It supports **captcha recognition (OCR)** and seat selection.

---

## Features

1. **Yanolja Login (Kakao Account)**
   - Clicks Kakao login button and handles authentication in a new tab
   - Automatically switches back to the main tab after login

2. **Interpark Ticket Login**
   - Clicks the login button and handles account authentication

3. **Ticket Booking Page Navigation & Date Selection**
   - Selects the desired year, month, and day
   - Automatically closes the booking popup

4. **Captcha Automation (OCR)**
   - Detects captcha images inside iframes
   - Sends images to a backend OCR server for recognition
   - Automatically inputs and submits the captcha text

5. **Seat Selection Automation**
   - Specify layer, row, and seat number
   - Clicks image map (`area`) and selects the seat

---

## Installation

1. **Install Python 3.10 or above**

2. **Install required libraries**
```bash
pip install undetected-chromedriver selenium selenium-stealth requests easyocr google-cloud-vision
