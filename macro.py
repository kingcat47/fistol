import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import re
from google.cloud import vision
import easyocr


# 크롬 옵션 설정 (detach 옵션 제거)
options = uc.ChromeOptions()
options.add_argument('--disable-popup-blocking')
options.add_argument("--window-size=1900,1000")
# 필요시 기존 로그인 세션 유지하려면 아래 주석 해제 후 경로 수정
# options.add_argument(r"user-data-dir=C:\Users\YourUserName\AppData\Local\Google\Chrome\User Data")

# undetected_chromedriver 드라이버 생성
driver = uc.Chrome(options=options, enable_cdp_events=True, incognito=True)

# selenium_stealth로 자동화 탐지 우회 설정
stealth(driver,
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# navigator.plugins 등 조작(자동화 노출 방지)
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});")

wait = WebDriverWait(driver, 15)

# 1. 야놀자 로그인 접속
yanolja_url = 'https://accounts.yanolja.com/'
driver.get(yanolja_url)

# 2. 카카오 로그인 버튼 클릭
kakao_login_button = wait.until(EC.element_to_be_clickable((
    By.CSS_SELECTOR, "div.KakaoLoginButton.flex.w-full.flex-row.items-center.justify-center.text-text-neutral-main.typography-subtitle-16-bold"
)))
time.sleep(0.5)
kakao_login_button.click()

# 3. 새 탭 전환 (네이버 로그인)
wait.until(lambda d: len(d.window_handles) > 1)
driver.switch_to.window(driver.window_handles[-1])

# 4. 네이버 로그인 입력
id_input = wait.until(EC.presence_of_element_located((By.NAME, 'loginId')))
id_input.clear()
id_input.send_keys('')

pw_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
pw_input.clear()
pw_input.send_keys('')

# 5. 로그인 버튼 클릭
login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"].btn_g.highlight')))
login_btn.click()

# 6. 원래 탭 복귀
time.sleep(3)
driver.switch_to.window(driver.window_handles[0])
time.sleep(2)#-d-ad-fas-dfas-df-sadf-sadfas-df-
# 7. 인터파크 티켓 메인 접속 후 로그인 버튼 클릭
interpark_ticket_url = "https://nol.interpark.com/ticket"
driver.get(interpark_ticket_url)

wait = WebDriverWait(driver, 15)
login_button = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[.//text()[contains(., '로그인')]]"
)))
login_button.click()

# 8. 원하는 티켓 상세 페이지로 이동
ticket_url_uuid = 25005777
want_ticket_url = "https://tickets.interpark.com/goods/"

full_url = want_ticket_url + str(ticket_url_uuid)
print(full_url)
driver.get(full_url)

# 9. 예매 안내 팝업 닫기 (JS 클릭으로 강제 클릭)
wait = WebDriverWait(driver, 10)
try:
    close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.popupCloseBtn.is-bottomBtn")))
    driver.execute_script("arguments[0].click();", close_btn)
except Exception as e:
    print("팝업 닫기(자바스크립트) 실패:", e)

target_day = 7
target_month = 9


while True:
    month_elem = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'li[data-view="month current"]')
    ))
    month_text = month_elem.text.strip()  # 예: "2025. 09"
    # month_text에서 월만 추출
    current_month = int(month_text.split('.')[1].strip())

    if current_month == target_month:
        break
    else:
        # 다음 달로 이동
        next_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'li[data-view="month next"]')
        ))
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(0.5)  # 동적 로딩 시간 대기

# 원하는 날짜 클릭 (days 영역에서 day 선택)
# days 영역 내 원하는 날짜 찾기
days = driver.find_elements(By.CSS_SELECTOR, 'ul[data-view="days"] li')
for d in days:
    day_text = d.text.strip()
    try:
        # 날짜가 숫자이고 원하는 날짜라면 클릭
        if day_text.isdigit() and int(day_text) == target_day:
            driver.execute_script("arguments[0].click();", d)
            break
    except:
        continue

# "예매하기" 버튼 요소 찾기
reserve_btn = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, 'a.sideBtn.is-primary')
))
# 클릭 (문제가 있으면 JS로도 시도 가능)
reserve_btn.click()
# 또는
# driver.execute_script("arguments[0].click();", reserve_btn)
#=====================================================================================
# 팝업이 새창으로 열리는 경우 창 전환
wait.until(lambda d: len(d.window_handles) > 1)
driver.switch_to.window(driver.window_handles[-1])
time.sleep(10)  # 팝업 완전 로딩 대기


import base64
from io import BytesIO
from PIL import Image
import easyocr
from selenium.common.exceptions import NoSuchElementException

# easyocr 리더 초기화 (언어는 'en'으로 설정)
# reader = easyocr.Reader(['en'])

# 팝업 새 창 전환 대기 및 이동
wait.until(lambda d: len(d.window_handles) > 1)
driver.switch_to.window(driver.window_handles[-1])
time.sleep(1)  # 팝업 완전 로딩 대기


# 캡챠 자동 처리 함수 정의
def solve_captcha(driver, wait, backend_url="http://localhost:5000"):
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"iframe 개수: {len(iframes)}")

    target_found = False
    captcha_img = None

    for i, frame in enumerate(iframes):
        driver.switch_to.default_content()
        driver.switch_to.window(driver.window_handles[-1])
        driver.switch_to.frame(frame)
        try:
            captcha_img = driver.find_element(By.ID, "imgCaptcha")
            print(f"[성공] imgCaptcha 발견, iframe index: {i}")
            target_found = True
            break
        except NoSuchElementException:
            continue

    if not target_found:
        print("[Error] imgCaptcha 태그를 가진 iframe을 찾지 못했습니다.")
        driver.switch_to.default_content()
        return False

    try:
        send_backend_start = time.time()
        src = captcha_img.get_attribute('src')
        if src and src.startswith('data:image'):
            base64_data = src.split(',')[1]

            response = requests.post(
                f"{backend_url}/api/ocr",
                json={'imageBase64': base64_data},
                timeout=5
            )
            response.raise_for_status()
            result = response.json()
            extracted_text = result.get('text', '').strip()
            extracted_text = re.sub(r'[^A-Za-z]', '', extracted_text)
            start_wait_time = time.time()
            print(f"[캡챠 OCR 인식 결과]: {extracted_text}")
            send_backend_end = time.time()
            send_backend = send_backend_end - send_backend_start
            print("걸린시간:", send_backend)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

#======================================================================================


            def switch_to_frame_containing_element(driver, by, value):
                driver.switch_to.default_content()

                def recursive_search_and_switch(depth=0):
                    try:
                        elem = driver.find_element(by, value)
                        print(f"요소 찾음, iframe depth: {depth}")
                        return True
                    except NoSuchElementException:
                        pass

                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for i, iframe in enumerate(iframes):
                        driver.switch_to.frame(iframe)
                        if recursive_search_and_switch(depth + 1):
                            return True
                        driver.switch_to.parent_frame()
                    return False

                found = recursive_search_and_switch()
                return found

            driver.switch_to.default_content()

            # 먼저 캡챠 입력 필드가 어느 iframe에 있는지 재귀적으로 찾아서 그 프레임으로 전환
            found = switch_to_frame_containing_element(driver, By.ID, "txtCaptcha")

            if found:
                # 캡챠 입력 필드 찾음, 해당 프레임 컨텍스트 안에 있음

                # 요소를 찾는다
                captcha_input = driver.find_element(By.ID, "txtCaptcha")

                # 자바스크립트로 "캡챠 입력 필드가 클릭(포커스) 될 때까지 대기"하기 위한 변수 및 이벤트 리스너 등록
                driver.execute_script('''
                    window.userClickedCaptcha = false;  // 전역 변수로 플래그 생성
                    var input = document.getElementById('txtCaptcha');
                    if(input){
                        input.addEventListener('focus', function(){
                            window.userClickedCaptcha = true;  // 사용자가 클릭(포커스)하면 플래그 true로 변경
                        });
                    }
                ''')

                print("사용자가 캡챠 입력 필드를 클릭할 때까지 대기합니다...")
                start_time = time.time()

                # 백엔드 OCR 결과부터 대기 시작까지 소요 시간 출력
                elapsed_from_ocr_to_wait = start_time - start_wait_time
                print(f"OCR 결과 수신 후 대기 시작까지 소요 시간: {elapsed_from_ocr_to_wait:.3f}초")

                timeout = 120  # 최대 120초 대기
                start_time = time.time()

                # 사용자가 클릭(포커스)하기 전까지 폴링으로 상태 체크
                while time.time() - start_time < timeout:
                    user_clicked = driver.execute_script('return window.userClickedCaptcha;')
                    if user_clicked:
                        print("사용자가 캡챠 입력 필드를 클릭했습니다!")
                        break
                    time.sleep(0.5)
                else:
                    print("시간 초과로 사용자의 클릭을 감지하지 못했습니다.")
                    # 필요시 예외처리 혹은 함수 종료

                # 사용자가 클릭한 뒤, 자동으로 백엔드 OCR에서 받은 텍스트를 입력
                captcha_input.clear()  # 만약 기존 텍스트가 있다면 클리어
                captcha_input.send_keys(extracted_text)
                print("[자동 입력] 백엔드 OCR 텍스트 입력 완료")

            else:
                print("캡챠 입력 필드를 찾지 못했습니다.")

            try:
                submit_btn = driver.find_element(By.XPATH, "//a[contains(text(),'입력완료')]")
                driver.execute_script("arguments[0].click();", submit_btn)  # 수정된 부분
                print("[캡챠] 입력완료 버튼 클릭 성공")
            except Exception as e:
                print("[Error] 입력완료 버튼 클릭 실패:", e)

            driver.switch_to.default_content()
            return True

        else:
            print("[Error] imgCaptcha src가 base64 데이터가 아니거나 src가 없습니다.")
    except requests.exceptions.RequestException as e:
        print("[Error] 백엔드 OCR 요청 실패:", e)
    except Exception as e:
        print(f"[Error] 캡챠 처리 중 오류 발생: {e}")

    driver.switch_to.default_content()
    return False



# 예제: 여기서 야놀자 로그인 및 다른 작업 수행 후 캡챠 처리 호출 부분
# (이하 생략 - 기존 코드 유지하면서 필요시 solve_captcha 함수 호출)

# 예시로 캡챠 호출만 첨부
success = solve_captcha(driver, wait, "http://localhost:5000")
if success:
    print("캡챠 자동 입력 완료")
else:
    print("캡챠 자동 입력 실패")