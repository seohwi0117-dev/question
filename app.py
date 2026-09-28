import streamlit as st
import pandas as pd
import random
import time
import re

st.set_page_config(
    page_title="도전! 속담 이어말하기",
    page_icon="🎉",
    layout="centered"
)

st.markdown("""
<style>
    .big-font {
        font-size:40px !important;
        font-weight: bold;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 20px;
    }
    .stat-box {
        background-color: #F8F9F9;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .hint-text {
        color: #E74C3C;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }
    .stTextInput>div>div>input {
        font-size: 24px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        font-size: 20px;
        height: 50px;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'hint_count' not in st.session_state:
        st.session_state.hint_count = 0
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_q_idx' not in st.session_state:
        st.session_state.current_q_idx = 0
    if 'end_time' not in st.session_state:
        st.session_state.end_time = 0
    if 'hint_used_current_q' not in st.session_state:
        st.session_state.hint_used_current_q = False
    if 'show_hint' not in st.session_state:
        st.session_state.show_hint = False
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False

@st.cache_data
def load_data():
    try:
        # question.csv 파일 로드 (예시 데이터를 기본으로 제공하거나 파일이 없을 경우 대비)
        df = pd.read_csv('question.csv', encoding='utf-8')
        return df.to_dict('records')
    except FileNotFoundError:
        # 파일이 없을 경우 기본 속담 데이터 제공
        st.warning("question.csv 파일을 찾을 수 없어 기본 데이터로 실행합니다.")
        return [
            {"prefix": "가는 날이", "answer": "장날이다"},
            {"prefix": "등잔 밑이", "answer": "어둡다"},
            {"prefix": "소 잃고", "answer": "외양간 고친다"},
            {"prefix": "원숭이도", "answer": "나무에서 떨어진다"},
            {"prefix": "티끌 모아", "answer": "태산"},
            {"prefix": "누워서", "answer": "떡 먹기"},
            {"prefix": "꿩 대신", "answer": "닭"},
            {"prefix": "우물 안", "answer": "개구리"},
            {"prefix": "천 리 길도", "answer": "한 걸음부터"},
            {"prefix": "돌다리도", "answer": "두들겨 보고 건너라"}
        ]

def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    chosung = ""
    for char in text:
        if '가' <= char <= '힣':
            # 한글 유니코드 공식: (초성 * 21 * 28) + (중성 * 28) + 종성 + 44032
            ch1 = (ord(char) - ord('가')) // 588
            chosung += CHOSUNG_LIST[ch1]
        elif char.isspace():
            chosung += " "
        else:
            chosung += char
    return chosung

def check_answer(user_input, correct_answer):
    # 특수문자 제거 및 공백 제거
    def normalize_text(text):
        text = re.sub(r'[^가-힣a-zA-Z0-9]', '', text)
        return text
    
    normalized_input = normalize_text(user_input)
    normalized_answer = normalize_text(correct_answer)
    
    return normalized_input == normalized_answer

def start_game(time_limit):
    st.session_state.game_started = True
    st.session_state.score = 0
    st.session_state.hint_count = 0
    st.session_state.current_q_idx = 0
    st.session_state.game_over = False
    
    # 문제 랜덤 섞기
    all_questions = load_data()
    random.shuffle(all_questions)
    st.session_state.questions = all_questions
    
    # 종료 시간 설정
    st.session_state.end_time = time.time() + time_limit

def submit_answer():
    if not st.session_state.user_answer:
        return

    user_input = st.session_state.user_answer
    current_q = st.session_state.questions[st.session_state.current_q_idx]
    correct_answer = current_q['answer']
    
    if check_answer(user_input, correct_answer):
        st.session_state.score += 1
        st.success("정답입니다! 👏")
        st.balloons()
    else:
        st.error(f"오답입니다! 정답은 '{correct_answer}' 였습니다. 🥲")
    
    # 상태 초기화 및 다음 문제로
    time.sleep(1.5) # 메시지를 잠시 보여주기 위해 대기
    st.session_state.current_q_idx += 1
    st.session_state.hint_used_current_q = False
    st.session_state.show_hint = False
    st.session_state.user_answer = "" # 입력창 초기화

init_session_state()

# 1. 시작 화면
if not st.session_state.game_started:
    st.markdown("<div class='big-font'>🎮 도전! 속담 이어말하기 🎮</div>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 게임 설명
        - 속담의 앞부분을 보고 뒷부분을 맞춰보세요!
        - 띄어쓰기는 틀려도 괜찮아요.
        - 모를 때는 **힌트(초성)**를 사용할 수 있어요. (최대 2번)
        - 제한 시간 안에 최대한 많은 속담을 맞춰보세요!
        """)
        
        st.write("")
        time_limit = st.slider("⏱️ 제한 시간 설정 (초)", min_value=30, max_value=300, value=60, step=10)
        
        st.write("")
        if st.button("🚀 게임 시작하기", use_container_width=True):
            start_game(time_limit)
            st.rerun()

# 2. 게임 화면
elif st.session_state.game_started and not st.session_state.game_over:
    
    # 남은 시간 계산
    time_left = max(0, int(st.session_state.end_time - time.time()))
    
    if time_left == 0 or st.session_state.current_q_idx >= len(st.session_state.questions):
        st.session_state.game_over = True
        st.rerun()

    # 상단 통계 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='stat-box'>🏆 점수: {st.session_state.score}점</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-box'>⏱️ 남은 시간: <span style='color:red;'>{time_left}초</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-box'>💡 힌트 남은 횟수: {2 - st.session_state.hint_count}회</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    # 현재 문제 표시
    current_q = st.session_state.questions[st.session_state.current_q_idx]
    
    st.markdown(f"<div class='big-font'>{current_q['prefix']} ...</div>", unsafe_allow_html=True)
    
    # 힌트 표시 영역
    if st.session_state.show_hint:
        chosung_hint = get_chosung(current_q['answer'])
        st.markdown(f"<div class='hint-text'>힌트: {chosung_hint}</div>", unsafe_allow_html=True)
    else:
        st.write("") # 공간 차지용
        
    st.write("")
    
    # 정답 입력 및 버튼 영역
    form_col, button_col = st.columns([3, 1])
    
    with form_col:
        # on_change 콜백을 사용하여 엔터키 입력 시 submit_answer 실행
        st.text_input("정답을 입력하세요!", key="user_answer", on_change=submit_answer, placeholder="뒷부분을 이어 써주세요")
    
    with button_col:
        st.write("") # 정렬용 공백
        st.write("")
        # 제출 버튼 (text_input의 엔터와 같은 기능)
        if st.button("정답 제출", use_container_width=True):
            if st.session_state.user_answer:
                submit_answer()
                st.rerun()

    st.write("")
    
    # 힌트 버튼
    hint_disabled = st.session_state.hint_count >= 2 or st.session_state.hint_used_current_q
    
    if st.button("💡 힌트 보기 (초성)", disabled=hint_disabled, use_container_width=True):
        st.session_state.hint_count += 1
        st.session_state.hint_used_current_q = True
        st.session_state.show_hint = True
        st.rerun()
        
    # 1초마다 화면을 갱신하여 타이머 업데이트 (Streamlit 특성상 깜빡임이 발생할 수 있음)
    time.sleep(1)
    st.rerun()

# 3. 게임 종료 화면
elif st.session_state.game_over:
    st.markdown("<div class='big-font'>🛑 게임 종료! 🛑</div>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>최종 점수: {st.session_state.score}점</h2>", unsafe_allow_html=True)
        st.write("")
        
        if st.button("🔄 다시 하기", use_container_width=True):
            st.session_state.game_started = False
            st.rerun()
