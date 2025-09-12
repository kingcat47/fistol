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

# 3. 새 탭 전환 (카카오 로그인)
wait.until(lambda d: len(d.window_handles) > 1)
driver.switch_to.window(driver.window_handles[-1])

# 4. 카카오 로그인 입력
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
time.sleep(2)


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

target_day = 15
target_month = 9


# month 영역 내 원하는 달 찾기
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
time.sleep(0.3)  # 팝업 완전 로딩 대기


from selenium.common.exceptions import NoSuchElementException

# 팝업 새 창 전환 대기 및 이동
wait.until(lambda d: len(d.window_handles) > 1)
driver.switch_to.window(driver.window_handles[-1])
time.sleep(1)  # 팝업 완전 로딩 대기


def solve_captcha(driver, wait, backend_url="http://localhost:5000", max_retries=10):
    from selenium.common.exceptions import NoSuchElementException
    import time, re, requests

    attempt = 0
    while True:
        attempt += 1
        print(f"[캡챠 처리] 시도: {attempt}")

        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        target_found = False
        captcha_img = None

        # 1. 캡챠 이미지 iframe 탐색
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
            # 2. 캡챠 이미지 base64 추출 및 OCR 요청
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
                print(f"[캡챠 OCR 인식 결과]: {extracted_text}")

                # 3. 캡챠 입력 필드 iframe 탐색 (재귀)
                def switch_to_frame_containing_element(driver, by, value):
                    driver.switch_to.default_content()
                    def recursive_search_and_switch(depth=0):
                        try:
                            elem = driver.find_element(by, value)
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
                found = switch_to_frame_containing_element(driver, By.ID, "txtCaptcha")

                if not found:
                    print("캡챠 입력 필드를 찾지 못했습니다.")
                    driver.switch_to.default_content()
                    return False

                captcha_input = driver.find_element(By.ID, "txtCaptcha")

                # 첫 번째 시도는 사용자 입력 대기, 재시도부터는 바로 입력
                if attempt == 1:
                    driver.execute_script('''
                        window.userClickedCaptcha = false;
                        var input = document.getElementById('txtCaptcha');
                        if(input){
                            input.addEventListener('focus', function(){
                                window.userClickedCaptcha = true;
                            });
                        }
                    ''')
                    print("사용자가 캡챠 입력 필드를 클릭할 때까지 대기합니다...")
                    timeout = 120
                    start_time = time.time()
                    while time.time() - start_time < timeout:
                        user_clicked = driver.execute_script('return window.userClickedCaptcha;')
                        if user_clicked:
                            print("사용자가 캡챠 입력 필드를 클릭했습니다!")
                            break
                        time.sleep(0.5)
                    else:
                        print("시간 초과로 사용자의 클릭을 감지하지 못했습니다.")
                        # 재시도 바로 진행

                # OCR 결과 입력
                captcha_input.clear()
                captcha_input.send_keys(extracted_text)
                print("[자동 입력] 백엔드 OCR 텍스트 입력 완료")

                # 제출 버튼 클릭
                try:
                    submit_btn = driver.find_element(By.XPATH, "//a[contains(text(),'입력완료')]")
                    driver.execute_script("arguments[0].click();", submit_btn)
                    print("[캡챠] 입력완료 버튼 클릭 성공")
                except Exception as e:
                    print("[Error] 입력완료 버튼 클릭 실패:", e)

                driver.switch_to.default_content()

                # 4. 성공/실패 판별: 여기에 '캡챠가 맞았습니다' 여부 체크 추가 필요
                # 예: 성공시 특정 요소 존재, 경고창, 페이지 이동 등…
                # 아래는 예시 (실제 환경에 맞게 수정)
                time.sleep(1)
                # 예시: 에러 메시지 없으면 성공
                try:
                    # 실패시 "캡챠 불일치" 텍스트가 보이면 반복, 없으면 성공
                    error_elem = driver.find_element(By.XPATH, "//*[contains(text(),'캡챠 불일치')]")
                    print("[캡챠] 인식 오류로 재도전합니다.")
                    continue  # while true 반복
                except NoSuchElementException:
                    print("[캡챠] 성공적으로 입력됨")
                    return True

            else:
                print("[Error] imgCaptcha src가 base64 데이터가 아니거나 src가 없습니다.")
                return False
        except requests.exceptions.RequestException as e:
            print("[Error] 백엔드 OCR 요청 실패:", e)
            return False
        except Exception as e:
            print(f"[Error] 캡챠 처리 중 오류 발생: {e}")
            return False

    driver.switch_to.default_content()
    return False



# 예시로 캡챠 호출만 첨부
success = solve_captcha(driver, wait, "http://localhost:5000")
if success:
    print("캡챠 자동 입력 완료")
else:
    print("캡챠 자동 입력 실패")


#좌석 선택하는 부분

#원하는 자리 수
first_ticket = []
#몇층 몇번째줄 몇번째
layer = 2
lineNumber = 5
seatNumber = 28

def choiceSeat(layer, lineNumber, seatNumber):
    try:
        # 좌석 선택
        seat = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//li[@data-layer='{layer}'][@data-line='{lineNumber}'][@data-seat='{seatNumber}']"
        )))
        driver.execute_script("arguments[0].click();", seat)
        print(f"[좌석 선택] 층: {layer}, 줄: {lineNumber}, 좌석: {seatNumber}")
    except Exception as e:
        print(f"[Error] 좌석 선택 실패: {e}")
from selenium.webdriver.common.by import By

def click_area_in_iframes(driver, wait, area_alt_or_title="RGN002영역"):
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    found = False
    for i, frame in enumerate(iframes):
        driver.switch_to.default_content()
        driver.switch_to.window(driver.window_handles[-1])
        driver.switch_to.frame(frame)
        try:
            # area 태그 찾기 (alt 값으로)
            area = driver.find_element(By.XPATH, f"//area[@alt='{area_alt_or_title}']")
            # area 태그에 직접 click 이벤트 실행 (실제 브라우저에서 동작하려면 이 방식 필요)
            driver.execute_script("arguments[0].click();", area)
            print(f"[성공] iframe {i}번에서 area alt='{area_alt_or_title}' 클릭 완료")
            found = True
            driver.switch_to.default_content()
            break
        except NoSuchElementException:
            continue
    driver.switch_to.default_content()
    if not found:
        print("[실패] 해당 area 태그를 가진 iframe을 찾지 못했습니다.")
        return False
    return True



def select_layer_and_seat(driver, wait, layer, lineNumber, seatNumber):
    if layer != 1:
        success = click_area_in_iframes(driver, wait)
        if not success:
            print(f"{layer}층 이미지 클릭 실패")
            return False
        # 클릭 후 좌석 선택 함수 호출
        choiceSeat(layer, lineNumber, seatNumber)
    else:
        choiceSeat(layer, lineNumber, seatNumber)
    return True

select_layer_and_seat(driver,wait, layer, lineNumber, seatNumber)