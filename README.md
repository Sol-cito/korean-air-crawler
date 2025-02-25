<h2> 사용법 </h2>

1. 카카오 개발자 (https://developers.kakao.com/) 사이트 가입 및 키 획득
먼저 .exe 파일이 있는 동일한 directory에 input.txt 파일을 하나 만든다.
https://ongamedev.tistory.com/462 여기 블로그에 나와있는대로 따라해서 REST API KEY 와 Redirect URI(https://example.com/oauth 권장) 를 
input.txt 에 아래와 같은 format으로 입력한다.

Format)<br>
REST_KEY=123123123blahblah <br>
REDIRECT_URL=https://example.com/oauth

2. 실행파일을 실행하면 
"input.txt 파일을 읽습니다...
다음 URL을 웹 브라우저에 입력 후, 리다이렉트 된 페이지 주소 URL의 code= 값을 입력해주세요" 라는 안내와 함께 링크가 제공되는데,
해당 링크에 접속하면 특정 주소로 이동하게 되고, 이 주소는 'https://example.com/oauth?code=blahblah...' 형식으로 되어있다.
여기서 blahblah... 에 해당하는 코드를 복사한 후 실행파일에 붙여넣는다. 이 과정은 Kakao talk 메시지 API를 보내는데 필요한 토큰을 발급하는 과정이다.
토큰이 발급되면 kakao_token.json 이라는 파일이 생성될 것이다.

3. 대한항공 ID와 비밀번호를 입력하고, 크롤링 종료 month를 입력한다. 여기서 크롤링 시작 일자는 크롤링 시작 일로부터 +1로 고정되어 있으므로,
입력할 필요 없이 종료 month만 입력하면 된다. 예를들어 종료 month가 07월이고 실행 일자가 2월 15일이면 2월 15일~07월 사이의 비즈니스석을 크롤링한다.

4. 입력하면 셀레니움이 전체화면으로 실행되고 결과를 카카오톡 메시지로 보낸다. 카카오톡 메시지는 200자 길이제한이 있으므로 긴 메시지는 200자씩 끊어서 multiple messages로 보내진다.

5. 셀레니움이 실행되고 있는동안은 브라우저를 클릭이나 키보드 입력 없이 가만히 두는 것이 신상에 좋다. 또한 컴퓨터 절전모드 등등을 해제해야 한다.
셀레니움이 실행되는 크롬에 예상치 못한 유저 혹은 시스템의 interrupt 가 발생하면 셀레니움에 예상치 못한 에러가 발생하기 때문이다.

6. 유저가 직접 커맨드를 종료하기 전까지 크롤링이 무한정 계속되지만, 크롤링 중간에 예상치 못한 에러가 발생 시 최대 5번의 재시도를 하며, 5번이 넘는 에러가 나면 프로그램이 종료된다.


- 실행파일 만드는 커맨드: pyinstaller main.py (dist 폴더에 exe 생성됨)