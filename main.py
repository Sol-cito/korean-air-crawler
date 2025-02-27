import time, os
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import requests
import json
from selenium.webdriver.common.by import By


class CrawlingOption:
    def __init__(self,
                 all_airport_in_europe,
                 start_search_month,
                 start_search_date,
                 end_search_month,
                 already_adjacent_days_btn_selected=False):
        self.all_airport_in_europe = all_airport_in_europe
        self.start_search_month = start_search_month
        self.start_search_date = start_search_date
        self.end_search_month = end_search_month
        self.already_adjacent_days_btn_selected = already_adjacent_days_btn_selected


def format_month_number(number):
    if 1 <= number <= 9:
        return str(number).zfill(2)
    else:
        return str(number)


def login(driver, id, pw):
    try:
        driver.get('https://www.koreanair.com/login?')
        time.sleep(10)

        cookie_allow_btn_from_shadow_root = driver.execute_script(
            """
                var shadowRoot = document.querySelector('kc-global-cookie-banner').shadowRoot;
                var agreeButton = shadowRoot.querySelector('button');
                return agreeButton;
                """
        )

        cookie_allow_btn_from_shadow_root.click()
        time.sleep(1)

        id_input = driver.find_element(By.XPATH, "//*[contains(@id, 'textinput')]")
        id_input.send_keys(id)
        time.sleep(1)

        pw_input = driver.find_element(By.XPATH, "//*[contains(@id, 'passwordinput')]")
        pw_input.send_keys(pw)
        time.sleep(1)

        login_btn = driver.find_element(By.CLASS_NAME, "login__submit-act")
        login_btn.click()
        time.sleep(30)

        login_failed_message = driver.find_elements(By.XPATH,
                                                    '//*[@id="shell-root"]/app-root/div/ke-login/ke-basic-layout/div[1]/ke-login-cont/ke-login-pres/div/form/div/div/div/div[1]/ke-error/div/p/em')
        if len(login_failed_message) > 0:
            raise Exception('[Error] 일치하는 회원정보가 없습니다. 아이디 또는 비밀번호를 확인해 주세요.')

        password_change_pass_cnt = 0

        while password_change_pass_cnt <= 5:
            password_change_pass_cnt += 1

            not_pw_change_btn = driver.find_elements(By.XPATH, '//*[@id="password-change"]/div/div/div/button[1]')
            if len(not_pw_change_btn) == 0:
                time.sleep(1)
                continue
            else:
                not_pw_change_btn[0].click()
                time.sleep(1)
                break

    except Exception as e:
        print(f"셀레니움 로그인 에러 발생: {e}")
        raise e


def initialize_airport():
    departure_btn = driver.find_element(By.XPATH, "//*[contains(@id, 'departureBtn')]")
    departure_btn.click()
    time.sleep(1)

    airport_search_input = driver.find_element(By.XPATH, "//*[contains(@class, 'auto-search__text')]")
    airport_search_input.click()
    time.sleep(1)

    airport_search_input.send_keys("DAD")  # 다낭으로 초기화
    airport_search_input.send_keys(Keys.ENTER)
    time.sleep(1)

    destination_btn = driver.find_element(By.XPATH, "//*[contains(@id, 'destinationBtn')]")
    destination_btn.click()
    time.sleep(1)

    airport_search_input = driver.find_element(By.XPATH, "//*[contains(@class, 'auto-search__text')]")
    airport_search_input.click()
    time.sleep(1)

    airport_search_input.send_keys("GUM")  # 괌으로 초기화
    airport_search_input.send_keys(Keys.ENTER)
    time.sleep(1)


def search_flight(driver, departure_airport, departure_month, dest_airport, crawlingOption):
    try:
        driver.get('https://www.koreanair.com/booking/search')

        time.sleep(5)

        mileage_btn = driver.find_element(By.XPATH, '//*[@id="tabBonusTrip"]')
        mileage_btn.click()
        time.sleep(1)

        oneway_btn = driver.find_elements(By.TAG_NAME, 'label')
        oneway_btn[1].click()
        time.sleep(1)

        # 출발, 도착 초기화
        initialize_airport()

        departure_btn = driver.find_element(By.XPATH, "//*[contains(@id, 'departureBtn')]")
        departure_btn.click()
        time.sleep(1)

        airport_search_input = driver.find_element(By.XPATH, "//*[contains(@class, 'auto-search__text')]")
        airport_search_input.click()
        time.sleep(1)

        airport_search_input.send_keys(departure_airport)
        airport_search_input.send_keys(Keys.ENTER)
        time.sleep(1)

        destination_btn = driver.find_element(By.XPATH, "//*[contains(@id, 'destinationBtn')]")
        destination_btn.click()
        time.sleep(1)

        airport_search_input = driver.find_element(By.XPATH, "//*[contains(@class, 'auto-search__text')]")
        airport_search_input.click()
        time.sleep(1)

        airport_search_input.send_keys(dest_airport)
        airport_search_input.send_keys(Keys.ENTER)
        time.sleep(1)

        calendar_btn = driver.find_element(By.CLASS_NAME, "booking-new__aligner-s-inner")
        calendar_btn.click()
        time.sleep(1)

        if not crawlingOption.already_adjacent_days_btn_selected:
            adjacent_days_btn = driver.find_elements(By.XPATH, "//*[contains(@class, 'switch')]")
            adjacent_days_btn[3].click()
            time.sleep(1)
            crawlingOption.already_adjacent_days_btn_selected = True

        departure_dates_on_calendar = driver.find_element(By.ID, f"month2025{departure_month}") \
            .find_element(By.TAG_NAME, 'table') \
            .find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'td')

        for e in departure_dates_on_calendar:
            if str(crawlingOption.start_search_date) in e.text:
                date_btn = e
                date_btn.click()
                time.sleep(1)
                break

        confirm_dialog_btn = driver.find_element(By.XPATH, "//*[contains(@class, 'dialog__confirm')]")
        confirm_dialog_btn.click()
        time.sleep(1)

        booking_search_btn = driver.find_element(By.XPATH, "//*[contains(@id, 'bookingGateOnSearch')]")
        booking_search_btn.click()
        time.sleep(1)

    except Exception as e:
        print(f"셀레니움 flight search 에러 발생: {e}")
        raise e


def check_business_seat(target_month, start_search_date):
    crawling_target_date_message = " - 크롤링 대상 date : "
    try:
        dates_on_calendar = driver.find_element(By.TAG_NAME, 'table') \
            .find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'td')

        prev_month_res = []
        target_month_res = []
        next_month_res = []

        first_date_found = False
        is_date_prev_month = False
        has_next_month_started = False

        for td in dates_on_calendar:
            td_date_and_seats = str(td.text)

            td_date_by_slicing = td_date_and_seats.split("\n")[0][-2:]

            if len(td_date_and_seats) < 2: continue
            if not first_date_found:
                first_date_found = True
                if int(td_date_by_slicing) > start_search_date:
                    is_date_prev_month = True

            if (f"{str(target_month)}/01" in td_date_and_seats) or (f"{str(target_month)}월 01" in td_date_and_seats):
                is_date_prev_month = False
                date = "01"
            elif (f"{str(target_month + 1)}/01" in td_date_and_seats) or (
                    f"{str(target_month + 1)}월 01" in td_date_and_seats):
                is_date_prev_month = False
                has_next_month_started = True
                date = "01"
            else:
                date = td_date_by_slicing

            # test
            if is_date_prev_month:
                crawling_target_date_message += f"{target_month - 1}월 {date}일/"
            elif not has_next_month_started:
                crawling_target_date_message += f"{target_month}월 {date}일/"
            else:
                crawling_target_date_message += f"{target_month + 1}월 {date}일/"

            if "프레스티지석" in td_date_and_seats:
                if is_date_prev_month:
                    prev_month_res.append(date)
                elif not has_next_month_started:
                    target_month_res.append(date)
                else:
                    next_month_res.append(date)

        print(crawling_target_date_message + "\n")
        return prev_month_res, target_month_res, next_month_res
    except Exception as e:
        print(f"셀레니움 check_business_seat 에러 발생: {e}")
        raise e


def check_all_the_possible_business_seats_in_a_loop(departure_airport, dest_airport, crawlingOption):
    business_res_dict = dict(
        zip([i for i in range(crawlingOption.start_search_month, crawlingOption.end_search_month + 1)],
            [[] for _ in range(crawlingOption.start_search_month, crawlingOption.end_search_month + 1)]))

    try:
        for i in range(start_search_month, end_search_month + 1):
            search_flight(driver=driver, departure_airport=departure_airport, departure_month=format_month_number(i),
                          dest_airport=dest_airport,
                          crawlingOption=crawlingOption)

            time.sleep(30)  # search 결과 로딩 딜레이

            no_nore_flight_searchable = driver.find_elements(By.XPATH, '//*[@id="panelBonusTrip"]/div/div/p/em')
            if len(no_nore_flight_searchable) > 0:
                print(f'\n{departure_airport}발 {dest_airport}도착 편 {i}월의 주변 일자까지 만석이거나 운항편이 없으므로 해당 노선 크롤링 종료.')
                break

            prev_month_res, target_month_res, next_month_res = check_business_seat(target_month=i,
                                                                                   start_search_date=crawlingOption.start_search_date)

            for prev_month_date_with_business in prev_month_res:
                if i - 1 < start_search_month: break
                res_in_month = business_res_dict.get(i - 1)
                if prev_month_date_with_business not in res_in_month:
                    res_in_month.append(prev_month_date_with_business)
            for target_month_date_with_business in target_month_res:
                res_in_month = business_res_dict.get(i)
                if target_month_date_with_business not in res_in_month:
                    res_in_month.append(target_month_date_with_business)

            if crawlingOption.start_search_month == crawlingOption.end_search_month:
                # business_res_dict.get(i + 1) 가 Null이므로 skip
                continue

            for next_month_date_with_business in next_month_res:
                res_in_month = business_res_dict.get(i + 1)
                if next_month_date_with_business not in res_in_month:
                    res_in_month.append(next_month_date_with_business)
            time.sleep(1)

        print(
            f'\n{departure_airport}출발 {dest_airport}도착 노선의 {crawlingOption.start_search_month}월 - {crawlingOption.end_search_month}월 비즈니스 좌석 크롤링 결과:')
        print(business_res_dict)
        return business_res_dict

    except Exception as e:
        print(f"셀레니움 check_all_the_possible_business_seats_in_a_loop 에러 발생: {e}")
        raise e


def get_back_to_the_initial_month_in_calendar(driver, initial_month, start_search_date):
    try:
        driver.get('https://www.koreanair.com/booking/search')
        time.sleep(5)

        calendar_btn = driver.find_element(By.CLASS_NAME, "booking-new__aligner-s-inner")
        calendar_btn.click()
        time.sleep(1)

        while True:
            displayed_months = driver.find_elements(By.CLASS_NAME, "datepicker__month")
            if initial_month in [int(displayed_months[0].text[:-1]), int(displayed_months[1].text[:-1])]:
                break
            back_btn = driver.find_element(By.CLASS_NAME, "datepicker__prev")
            back_btn.click()
            time.sleep(3)

        departure_dates_on_calendar = driver.find_element(By.ID, f"month2025{format_month_number(initial_month)}") \
            .find_element(By.TAG_NAME, 'table') \
            .find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'td')

        for e in departure_dates_on_calendar:
            if str(start_search_date) in e.text:
                date_btn = e
                date_btn.click()
                time.sleep(1)
                break

        confirm_dialog_btn = driver.find_element(By.XPATH, "//*[contains(@class, 'dialog__confirm')]")
        confirm_dialog_btn.click()
        time.sleep(1)
    except Exception as e:
        print(f"셀레니움 get_back_to_the_initial_month_in_calendar 에러 발생: {e}")
        raise e


def crawling_in_the_loop_with_airport_list(crawlingOption):
    crawling_result_in_dictionary = {}

    try:
        # 출발공항이 인천, 도착 공항이 유럽 모든 공항
        print("-크롤링 시작 - 출발공항이 인천, 도착 공항이 유럽 모든 공항...\n")
        for european_airport in all_airport_in_europe:
            print(f"\n * 크롤링 노선 : 인천 --> {european_airport}\n")
            business_res_dict = check_all_the_possible_business_seats_in_a_loop(
                departure_airport="ICN",
                dest_airport=european_airport,
                crawlingOption=crawlingOption)

            crawling_result_in_dictionary[f"ICN-{european_airport}"] = business_res_dict

            get_back_to_the_initial_month_in_calendar(driver=driver, initial_month=crawlingOption.start_search_month,
                                                      start_search_date=crawlingOption.start_search_date)
        print("-인천발 크롤링 끝...\n")

        # 출발공항이 유럽 모든 공항, 도착 공항이 인천
        print("-크롤링 시작 - 출발공항이 유럽 모든 공항, 도착 공항이 인천...\n")
        for european_airport in all_airport_in_europe:
            print(f" {european_airport} --> 인천")
            check_all_the_possible_business_seats_in_a_loop(
                departure_airport=european_airport,
                dest_airport="ICN",
                crawlingOption=crawlingOption)

            crawling_result_in_dictionary[f"{european_airport}-ICN"] = business_res_dict

            get_back_to_the_initial_month_in_calendar(driver=driver, initial_month=crawlingOption.start_search_month,
                                                      start_search_date=crawlingOption.start_search_date)
        print("-유럽발 크롤링 끝...\n")

        return crawling_result_in_dictionary
    except Exception as e:
        print(f"셀레니움 crawling_in_the_loop_with_airport_list 에러 발생: {e}")
        raise e


def get_search_date():
    # 오늘 날짜 가져오기
    today = datetime.today()

    # 오늘 날짜에 하루를 더한 날짜 계산
    next_day = today + timedelta(days=1)

    # 날짜가 다음 달로 넘어갈 경우 처리
    if next_day.month != today.month:
        start_search_month = next_day.month
        start_search_date = 1
    else:
        start_search_month = today.month
        start_search_date = today.day + 1

    return start_search_month, start_search_date


def get_kakaotalk_tokens(rest_api_key, redirect_uri, code):
    try:
        url = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': rest_api_key,
            'redirect_uri': redirect_uri,
            'code': code,
        }

        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"[Error] Kakao 토큰 발행 실패 - {response.text}")
        tokens = response.json()

        # 발행된 토큰 저장
        with open("kakao_token.json", "w") as kakao:
            json.dump(tokens, kakao)
    except Exception as e:
        print(f"get_kakaotalk_tokens 에러 발생: {e}")
        raise e


def get_new_access_token_by_refresh_token(rest_api_key):
    url = 'https://kauth.kakao.com/oauth/token'

    try:
        # 발행한 토큰 불러오기
        with open("kakao_token.json", "r") as kakao:
            tokens = json.load(kakao)

        data = {
            "grant_type": "refresh_token",
            "client_id": rest_api_key,
            "refresh_token": tokens["refresh_token"]
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"[Error] Kakao refresh 토큰 활용 실패 - {response.text}")
        new_tokens = response.json()
        with open("kakao_token.json", "w") as kakao:
            json.dump(new_tokens, kakao)

    except Exception as e:
        print(f"get_new_access_token_by_refresh_token 에러 발생: {e}")
        raise e


def send_kakao_talk_message_to_myself(message_content, rest_api_key, redirect_uri):
    try:
        while True:
            # 발행한 토큰 불러오기
            with open("kakao_token.json", "r") as kakao:
                tokens = json.load(kakao)

            url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

            headers = {
                "Authorization": "Bearer " + tokens["access_token"]
            }

            data = {
                'object_type': 'text',
                'text': message_content,
                'link': {
                    'web_url': 'https://developers.kakao.com',
                    'mobile_web_url': 'https://developers.kakao.com'
                },
            }

            data = {'template_object': json.dumps(data)}
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                print(f"Kakao talk 메시지 전송 완료 - 메시지: ({message_content})\n")
                break
            elif response.status_code == 400:
                get_new_access_token_by_refresh_token(rest_api_key=rest_api_key, redirect_uri=redirect_uri)
            else:
                raise Exception(f"[Error] 카카오톡 메시지 API 에러 - {response.text}\n")
    except Exception as e:
        print(f"send_kakao_talk_message_to_myself 에러 발생: {e}")
        raise e


def generate_kakao_message(crawling_result_in_dictionary, all_airport_mapping_dict):
    try:
        message = "<대한항공 비즈니스석 크롤링 결과>\n"
        idx = 1
        for itinerary in list(crawling_result_in_dictionary.keys()):
            airport_pair = itinerary.split("-")
            airport_names = [all_airport_mapping_dict.get(code, code) for code in airport_pair]  # 공항 코드 -> 공항명 변환
            itinerary_in_korean = "-".join(airport_names)  # '공항명-공항명' 형식으로 변환

            message += f"{idx}. {itinerary_in_korean}\n"

            each_dict_of_itinerary = crawling_result_in_dictionary.get(itinerary)

            if len(list(each_dict_of_itinerary.keys())) == 0:
                message += "기간 내 비즈니스석 없음.\n"
                continue

            for month in list(each_dict_of_itinerary.keys()):
                if len(each_dict_of_itinerary.get(month)) == 0: continue
                available_business_seat_dates = ", ".join(each_dict_of_itinerary.get(month))
                message += f" - {month}월 : {available_business_seat_dates}일\n"
            idx += 1
        return message
    except Exception as e:
        print(f"generate_kakao_message 에러 발생: {e}")
        raise e


if __name__ == '__main__':
    try:
        rest_api_key = ""
        redirect_uri = ""

        print("input.txt 파일을 읽습니다...\n")
        f = open("./input.txt", 'r', encoding='utf-8')
        lines = f.readlines()
        for line in lines:
            if "REST_KEY" in line:
                rest_api_key = line.replace("REST_KEY=", "").replace("\n", "")
            elif "REDIRECT_URL=" in line:
                redirect_uri = line.replace("REDIRECT_URL=", "").replace("\n", "")
        f.close()

        print(
            f"다음 URL을 웹 브라우저에 입력 후, 리다이렉트 된 페이지 주소 URL의 code= 값을 입력해주세요 \n https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code\n")

        code = input('Code : ')

        print("Kakao talk 토큰 저장 중....")
        get_kakaotalk_tokens(rest_api_key=rest_api_key, redirect_uri=redirect_uri, code=code)
        print("Kakao talk 토큰 발급 완료.\n ")

        id = input('대한항공 ID : ')
        pw = input('비밀번호 : ')

        start_search_month, start_search_date = get_search_date()

        print(f"크롤링 시작 일자: {start_search_month}월 {start_search_date}일 (현재 날짜 +1 자동 입력)")
        end_search_month = int(input('크롤링 종료 month (두자리수로 입력해야 함. E.g. 2월은 02, 11월은 11.) : '))

        print("셀레니움 start!!!!!!!!!!!!!!!\n")

        options = Options()
        # 브라우저 꺼짐 방지 옵션
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(service=ChromeService(), options=options)
        # 전체화면
        driver.maximize_window()

        login(driver=driver, id=id, pw=pw)

        print("로그인 성공....")

        all_airport_in_europe = ["LHR", "FCO", "LIS", "MAD", "MXP", "BUD", "VIE", "AMS", "IST", "ZRH", "CDG", "PRG",
                                 "FRA"]

        all_airport_mapping_dict = {
            "LHR": "런던히드로",  # London Heathrow Airport
            "FCO": "로마",  # Leonardo da Vinci–Fiumicino Airport
            "LIS": "리스본",  # Lisbon Airport
            "MAD": "마드리드",  # Madrid Barajas Airport
            "MXP": "밀라노",  # Milan Malpensa Airport
            "BUD": "부다페스트",  # Budapest Airport
            "VIE": "비엔나",  # Vienna International Airport
            "AMS": "암스테르담",  # Amsterdam Airport Schiphol
            "IST": "이스탄불",  # Istanbul Airport
            "ZRH": "취리히",  # Zurich Airport
            "CDG": "샤를드골",  # Charles de Gaulle Airport
            "PRG": "프라하",  # Václav Havel Airport Prague
            "FRA": "프랑크푸르트"  # Frankfurt Airport
        }

        crawlingOption = CrawlingOption(
            all_airport_in_europe=all_airport_in_europe,
            start_search_month=start_search_month,
            start_search_date=start_search_date,
            end_search_month=end_search_month,
        )

        # 최대 5번의 재시도
        max_retries = 5
        retries = 0

        # infinite loop
        while True:
            try:
                start = time.time()
                crawling_result_in_dictionary = crawling_in_the_loop_with_airport_list(crawlingOption=crawlingOption)

                # 최종결과 - crawling_result_in_dictionary
                print("최종 크롤링 결과 : ")
                print(crawling_result_in_dictionary)
                print("\n")

                message_content = generate_kakao_message(crawling_result_in_dictionary=crawling_result_in_dictionary,
                                                         all_airport_mapping_dict=all_airport_mapping_dict)

                # 200자씩 나누어서 보내기
                max_kakao_message_length = 200
                for i in range(0, len(message_content), max_kakao_message_length):
                    chunk = message_content[i:i + max_kakao_message_length]
                    send_kakao_talk_message_to_myself(message_content=chunk, rest_api_key=rest_api_key,
                                                      redirect_uri=redirect_uri)

                # 크롤링 사이클 종료
                end = time.time()

                elapsed_time = end - start

                # timedelta로 변환하여 시, 분, 초, 밀리초로 출력
                formatted_time = str(timedelta(seconds=elapsed_time))

                # '0:00:00.000'과 같은 형식으로 표시
                print(f"-크롤링 종료. 수행시간 : {formatted_time}\n")
            except Exception as e:
                retries += 1
                print(f"[Error] 크롤링 중 에러가 발생했습니다. 재시도 중... (시도 횟수: {retries}/{max_retries})\n")
                print(f"에러 메시지: {e}\n ")
                if retries == max_retries:
                    print("[Error] 최대 재시도 횟수에 도달했습니다. 프로그램을 종료합니다.")
                    os.system('pause')
                    exit()

    except Exception as e:
        print("[Error] 크롤링 에러로 인해 프로그램을 종료함.\n ")
        print(e)
        os.system('pause')
        exit()
