import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By


class CrawlingOption:
    def __init__(self,
                 all_airport_in_europe,
                 start_search_month,
                 start_search_date,
                 end_search_month,
                 res_dict,
                 already_adjacent_days_btn_selected=False):
        self.all_airport_in_europe = all_airport_in_europe
        self.start_search_month = start_search_month
        self.start_search_date = start_search_date
        self.end_search_month = end_search_month
        self.res_dict = res_dict
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
        time.sleep(20)

        while True:
            login_failed_message = driver.find_elements(By.XPATH,
                                                        '//*[@id="shell-root"]/app-root/div/ke-login/ke-basic-layout/div[1]/ke-login-cont/ke-login-pres/div/form/div/div/div/div[1]/ke-error/div/p/em')
            if len(login_failed_message) > 0:
                raise Exception('[Error] 일치하는 회원정보가 없습니다. 아이디 또는 비밀번호를 확인해 주세요.')
            not_pw_change_btn = driver.find_elements(By.XPATH, '//*[@id="password-change"]/div/div/div/button[1]')
            if len(not_pw_change_btn) == 0:
                continue
            not_pw_change_btn[0].click()
            time.sleep(1)
            break

    except Exception as e:
        print(f"셀레니움 로그인 에러 발생: {e}")
        raise e


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


def check_business_seat(target_month):
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
        if len(td_date_and_seats) < 2: continue
        if not first_date_found:
            first_date_found = True
            if int(td_date_and_seats[:2]) > 15:
                is_date_prev_month = True

        if f"{str(target_month)}/01" in td_date_and_seats:
            is_date_prev_month = False
            date = "01"
        elif f"{str(target_month + 1)}/01" in td_date_and_seats:
            is_date_prev_month = False
            has_next_month_started = True
            date = "01"
        else:
            date = td_date_and_seats[:2]

        # test
        if is_date_prev_month:
            print(f"크롤링 대상 date : {target_month - 1}월 {date}일")
        elif not has_next_month_started:
            print(f"크롤링 대상 date : {target_month}월 {date}일")
        else:
            print(f"크롤링 대상 date : {target_month + 1}월 {date}일")

        if "프레스티지석" in td_date_and_seats:
            if is_date_prev_month:
                prev_month_res.append(date)
            elif not has_next_month_started:
                target_month_res.append(date)
            else:
                next_month_res.append(date)

    return prev_month_res, target_month_res, next_month_res


def check_all_the_possible_business_seats_in_a_loop(departure_airport, dest_airport, crawlingOption):
    try:
        for i in range(start_search_month, end_search_month + 1):
            search_flight(driver=driver, departure_airport=departure_airport, departure_month=format_month_number(i),
                          dest_airport=dest_airport,
                          crawlingOption=crawlingOption)

            time.sleep(30)  # search 결과 로딩 딜레이

            no_nore_flight_searchable = driver.find_elements(By.XPATH, '//*[@id="panelBonusTrip"]/div/div/p/em')
            if len(no_nore_flight_searchable) > 0:
                print(f'{departure_airport}발 {dest_airport}도착 편 {i}월의 주변 일자까지 만석이거나 운항편이 없으므로 해당 노선 크롤링 종료.')
                break

            prev_month_res, target_month_res, next_month_res = check_business_seat(target_month=i)

            for prev_month_date_with_business in prev_month_res:
                if i - 1 < start_search_month: break
                res_in_month = res_dict.get(i - 1)
                if prev_month_date_with_business not in res_in_month:
                    res_in_month.append(target_month_date_with_business)

            for target_month_date_with_business in target_month_res:
                res_in_month = res_dict.get(i)
                if target_month_date_with_business not in res_in_month:
                    res_in_month.append(target_month_date_with_business)
            for next_month_date_with_business in next_month_res:
                res_in_month = res_dict.get(i + 1)
                if next_month_date_with_business not in res_in_month:
                    res_in_month.append(next_month_date_with_business)
            time.sleep(1)

        print(
            f'{departure_airport}출발 {dest_airport}도착 노선의 {crawlingOption.start_search_month}월 - {crawlingOption.end_search_month}월 비즈니스 좌석 크롤링 결과:')
        print(crawlingOption.res_dict)

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
            if int(displayed_months[0].text[:-1]) == initial_month and int(displayed_months[1].text[:-1]) == initial_month + 1:
                break
            back_btn = driver.find_elements(By.XPATH, "//*[contains(@id, 'dialog-datepicker')]")[0] #이게 안잡힘.
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


def send_kakao_talk_message():
    return


def crawling_in_the_loop_with_airport_list(crawlingOption):
    try:
        # 출발공항이 인천, 도착 공항이 유럽 모든 공항
        print("-크롤링 시작 - 출발공항이 인천, 도착 공항이 유럽 모든 공항...")
        for european_airport in all_airport_in_europe:
            print(f" 인천 --> {european_airport}")
            check_all_the_possible_business_seats_in_a_loop(
                departure_airport="ICN",
                dest_airport=european_airport,
                crawlingOption=crawlingOption)
            get_back_to_the_initial_month_in_calendar(driver=driver, initial_month=crawlingOption.start_search_month,
                                                      start_search_date=crawlingOption.start_search_date)
        print("-인천발 크롤링 끝...")

        # 출발공항이 유럽 모든 공항, 도착 공항이 인천
        print("-크롤링 시작 - 출발공항이 유럽 모든 공항, 도착 공항이 인천...")
        for european_airport in all_airport_in_europe:
            print(f" {european_airport} --> 인천")
            check_all_the_possible_business_seats_in_a_loop(
                departure_airport=european_airport,
                dest_airport="ICN",
                crawlingOption=crawlingOption)
            get_back_to_the_initial_month_in_calendar(driver=driver, initial_month=crawlingOption.start_search_month,
                                                      start_search_date=crawlingOption.start_search_date)
        print("-유럽발 크롤링 끝...")
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


if __name__ == '__main__':
    try:
        id = input('대한항공 ID : ')
        pw = input('비밀번호 : ')

        start_search_month, start_search_date = get_search_date()

        print(f"크롤링 시작 일자: {start_search_month}월 {start_search_date}일 (현재 날짜 +1 자동 입력)")
        end_search_month = int(input('크롤링 종료 month (두자리수로 입력해야 함. E.g. 2월은 02, 11월은 11.) : '))

        res_dict = dict(zip([i for i in range(start_search_month, end_search_month + 1)],
                            [[] for i in range(start_search_month, end_search_month + 1)]))

        batch_range = int(input('크롤링 수행 간격 (분단위로 입력) : '))

        print("셀레니움 start...")

        options = Options()
        # 브라우저 꺼짐 방지 옵션
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(service=ChromeService(), options=options)
        # 전체화면
        # driver.maximize_window()

        login(driver=driver, id=id, pw=pw)

        print("로그인 성공....")

        all_airport_in_europe = ["LHR", "FCO", "LIS", "MAD", "MXP", "BUD", "VIE", "AMS", "IST", "ZRH", "CDG", "PRG",
                                 "FRA"]

        crawlingOption = CrawlingOption(
            all_airport_in_europe=all_airport_in_europe,
            start_search_month=start_search_month,
            start_search_date=start_search_date,
            end_search_month=end_search_month,
            res_dict=res_dict
        )

        # infinite loop
        while True:
            crawling_in_the_loop_with_airport_list(crawlingOption=crawlingOption)

            # 크롤링 사이클 종료
            print(f"-크롤링 대기 {batch_range}분...")
            time.sleep(batch_range * 60)

    except Exception as e:
        print("[Error] 크롤링 에러로 인해 프로그램을 종료함.")
        exit()
