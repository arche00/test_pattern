# Bead Road Pattern Analyzer

이 애플리케이션은 SVG 형식의 비드로드 데이터를 분석하여 패턴을 식별하고 통계를 생성합니다.

## 프로젝트 구조

```
.
├── parser.py           # 메인 애플리케이션 파일
├── pattern.json        # 패턴 정의 파일
├── pattern_analysis.db # SQLite 데이터베이스
└── requirements.txt    # 프로젝트 의존성
```

## 주요 기능

1. SVG 데이터 파싱
   - 15x6 그리드 형태의 비드로드 데이터 파싱
   - Banker(B), Player(P), Tie(T) 결과 식별

2. 패턴 분석
   - 3칸 단위로 이동하며 그룹 분석
   - 각 그룹별 상단(1,2,3)과 하단(1,2,3,4) 패턴 식별
   - pattern.json 파일의 정의에 따른 패턴 매칭

3. 통계 기능
   - 전체 기록 통계 (100개 이하일 경우)
   - 최근 3시간 또는 최근 100개 중 큰 수의 데이터 기반 통계
   - P1, P2 패턴별 출현 빈도 분석

## 설치 및 실행

1. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행:
```bash
streamlit run parser.py
```

## 새로운 대화에서 컨텍스트 활용하기

1. 코드베이스 탐색:
   ```python
   # parser.py의 주요 상수 및 설정
   TABLE_WIDTH = 15
   TABLE_HEIGHT = 6
   CELL_BANKER = 'b'
   CELL_PLAYER = 'p'
   CELL_TIE = 't'
   ```

2. 데이터베이스 구조:
   ```sql
   -- pattern_analysis.db 테이블 구조
   CREATE TABLE pattern_records (
       round INTEGER PRIMARY KEY AUTOINCREMENT,
       timestamp TEXT,        -- YYMMDDHH 형식
       group_range TEXT,      -- "시작-끝" 형식
       pattern1 TEXT,         -- 상단 패턴
       result1 TEXT,         -- 상단 결과
       pattern2 TEXT,         -- 하단 패턴
       result2 TEXT          -- 하단 결과
   )
   ```

3. 패턴 정의:
   - `pattern.json` 파일에서 패턴 그룹 정의 확인
   - groupA와 groupB로 구분된 패턴 시퀀스 참조

## 주요 업데이트 내역

- 패턴 분석 기록 UI 개선
- 통계 기능 추가 (최근 3시간/100개 기준)
- 일괄 저장 기능 구현
- 미사용 파일 아카이브 처리 (/archive) 