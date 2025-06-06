import streamlit as st
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import json

# Database setup
def init_db():
    conn = sqlite3.connect('pattern_analysis.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pattern_records (
            round INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            group_range TEXT,
            pattern1 TEXT,
            result1 TEXT,
            pattern2 TEXT,
            result2 TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database when the app starts
init_db()

# Function to save pattern analysis results
def save_pattern_record(group_range, pattern_123, pattern_1234):
    # Format timestamp as YYMMDDHHMM
    current_time = datetime.now()
    timestamp = current_time.strftime("%y%m%d%H%M")
    
    # Process patterns
    pattern1 = pattern_123[:2] if len(pattern_123) >= 2 else ''
    result1 = pattern_123[2] if len(pattern_123) >= 3 else ''
    pattern2 = pattern_1234[:3] if len(pattern_1234) >= 3 else ''
    result2 = pattern_1234[3] if len(pattern_1234) >= 4 else ''
    
    try:
        conn = sqlite3.connect('pattern_analysis.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO pattern_records 
            (timestamp, group_range, pattern1, result1, pattern2, result2)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, group_range, pattern1, result1, pattern2, result2))
        conn.commit()
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {str(e)}")
    finally:
        conn.close()

# Function to display pattern records
def display_pattern_records():
    try:
        conn = sqlite3.connect('pattern_analysis.db')
        c = conn.cursor()
        # 라운드 내림차순으로 정렬 (최신순)
        records = c.execute('SELECT * FROM pattern_records ORDER BY round DESC LIMIT 10').fetchall()
        conn.close()
        
        st.markdown("### 패턴 분석 기록")
        if records:
            # Create a table header
            st.markdown("""
            | 라운드 | 시간 | 그룹 범위 | 패턴1 | 결과1 | 패턴2 | 결과2 |
            |--------|------|-----------|--------|--------|--------|--------|""")
            
            # Add each record to the table
            for record in records:
                st.markdown(f"| {record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]} | {record[5]} | {record[6]} |")
        else:
            st.info("저장된 기록이 없습니다.")
    except Exception as e:
        st.error(f"데이터 조회 중 오류 발생: {str(e)}")

# Table dimensions
TABLE_WIDTH = 15
TABLE_HEIGHT = 6

# Cell types
CELL_BANKER = 'b'
CELL_PLAYER = 'p'
CELL_TIE = 't'
CELL_EMPTY = ''

# Pattern definitions
PATTERN_WIDTH = 2
PATTERN_TOP_ROWS = [0,1,2]
PATTERN_BOTTOM_ROWS = [3,4,5]

def parse_bead_road_svg(svg_code):
    soup = BeautifulSoup(svg_code, 'html.parser')
    grid = [['' for _ in range(TABLE_HEIGHT)] for _ in range(TABLE_WIDTH)]
    
    coordinates = soup.find_all('svg', attrs={'data-type': 'coordinates'})
    for coord in coordinates:
        x = int(float(coord.get('data-x', 0)))
        y = int(float(coord.get('data-y', 0)))
        text_elem = coord.find('text')
        if text_elem and text_elem.string:
            result = text_elem.string.strip()
            if 0 <= x < TABLE_WIDTH and 0 <= y < TABLE_HEIGHT:
                grid[x][y] = result.lower()
    
    return grid

def display_grid(grid):
    st.markdown("""
        <style>
        .grid-container { display: table; border-collapse: collapse; margin: 20px 0; }
        .grid-row { display: table-row; }
        .bead-road-cell { width: 40px; height: 40px; border: 1px solid black; display: table-cell; 
                         text-align: center; vertical-align: middle; font-family: monospace; }
        .banker { color: red; font-weight: bold; }
        .player { color: blue; font-weight: bold; }
        .tie { color: green; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    html_table = ['<div class="grid-container">']
    for y in range(6):
        html_table.append('<div class="grid-row">')
        for x in range(15):
            cell = grid[x][y]
            css_class = 'banker' if cell == 'b' else 'player' if cell == 'p' else 'tie' if cell == 't' else ''
            html_table.append(f'<div class="bead-road-cell {css_class}">{cell.upper() if cell else "&nbsp;"}</div>')
        html_table.append('</div>')
    html_table.append('</div>')
    
    st.markdown(''.join(html_table), unsafe_allow_html=True)

def get_pattern_positions():
    patterns = []
    pattern_number = 1
    
    for start_col in range(TABLE_WIDTH - PATTERN_WIDTH + 1):
        cols = (start_col, start_col + 1)
        
        top_pattern = {
            'pattern_number': pattern_number,
            'columns': cols,
            'rows': PATTERN_TOP_ROWS,
            'coordinates': [(cols[0], y) for y in PATTERN_TOP_ROWS] + [(cols[1], y) for y in PATTERN_TOP_ROWS]
        }
        patterns.append(top_pattern)
        pattern_number += 1
        
        bottom_pattern = {
            'pattern_number': pattern_number,
            'columns': cols,
            'rows': PATTERN_BOTTOM_ROWS,
            'coordinates': [(cols[0], y) for y in PATTERN_BOTTOM_ROWS] + [(cols[1], y) for y in PATTERN_BOTTOM_ROWS]
        }
        patterns.append(bottom_pattern)
        pattern_number += 1
    
    return patterns

def display_zones(zones):
    if not zones:
        st.info("표시할 그룹이 없습니다.")
        return
    
    first_zone = zones[0]
    st.markdown(f"### 첫 번째 그룹 (열 {first_zone['start_x'] + 1} ~ {first_zone['end_x'] + 1})")
    
    st.markdown("""
        <style>
        .zone-container { display: table; border-collapse: collapse; margin: 10px 0; }
        .zone-row { display: table-row; }
        .zone-cell { width: 40px; height: 40px; border: 1px solid black; display: table-cell; 
                    text-align: center; vertical-align: middle; font-family: monospace; }
        .banker { color: red; font-weight: bold; }
        .player { color: blue; font-weight: bold; }
        .tie { color: green; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    html_zone = ['<div class="zone-container">']
    for y in range(6):
        html_zone.append('<div class="zone-row">')
        for x in range(len(first_zone['zone_data'])):
            cell = first_zone['zone_data'][x][y]
            css_class = 'banker' if cell == 'b' else 'player' if cell == 'p' else 'tie' if cell == 't' else ''
            html_zone.append(f'<div class="zone-cell {css_class}">{cell.upper() if cell else "&nbsp;"}</div>')
        html_zone.append('</div>')
    html_zone.append('</div>')
    
    st.markdown(''.join(html_zone), unsafe_allow_html=True)
    
    st.markdown("### 첫 번째 그룹의 패턴")
    patterns = get_pattern_positions()
    first_group_patterns = [p for p in patterns if p['columns'][0] >= first_zone['start_x'] and p['columns'][1] <= first_zone['end_x']]
    
    for pattern in first_group_patterns:
        st.markdown(f"#### 패턴 {pattern['pattern_number']}")
        pattern_html = ['<div class="zone-container">']
        for y in pattern['rows']:
            pattern_html.append('<div class="zone-row">')
            for x in pattern['columns']:
                cell = first_zone['zone_data'][x - first_zone['start_x']][y]
                css_class = 'banker' if cell == 'b' else 'player' if cell == 'p' else 'tie' if cell == 't' else ''
                pattern_html.append(f'<div class="zone-cell {css_class}">{cell.upper() if cell else "&nbsp;"}</div>')
            pattern_html.append('</div>')
        pattern_html.append('</div>')
        st.markdown(''.join(pattern_html), unsafe_allow_html=True)

def divide_grid_into_overlapping_zones(grid, zone_width=3):
    zones = []
    for start_x in range(15 - zone_width + 1):
        end_x = start_x + zone_width
        zone_data = [[grid[x][y] for y in range(6)] for x in range(start_x, end_x)]
        if any(cell in {'b', 't', 'p'} for column in zone_data for cell in column):
            zones.append({
                'zone_data': zone_data,
                'start_x': start_x,
                'end_x': end_x - 1
            })
    return zones

def find_pattern_group(pattern_values):
    """
    pattern.json에서 패턴의 그룹 값을 찾습니다.
    
    Args:
        pattern_values (list): 패턴의 문자 리스트 (예: ['B', 'P', 'B', 'B', 'P', 'B'])
    
    Returns:
        str or None: 패턴의 그룹 값 ('a' 또는 'b'), 없으면 None
    """
    try:
        with open('pattern.json', 'r') as f:
            pattern_data = json.load(f)
        
        # 입력된 패턴을 소문자로 변환
        pattern_values = [v.lower() for v in pattern_values if v]  # 빈 문자열 제외
        
        # groupA와 groupB의 모든 패턴을 검사
        for group_name in ['groupA', 'groupB']:
            patterns = pattern_data['patterns'][group_name]
            for pattern in patterns:
                if pattern.get('sequence') == pattern_values:
                    return pattern.get('group', group_name[5].lower())  # group 값이 없으면 'a' 또는 'b' 반환
        
        return None
    except Exception as e:
        st.error(f"패턴 그룹 검색 중 오류 발생: {str(e)}")
        return None

def get_pattern_values(grid, pattern_positions):
    """
    패턴의 좌표를 사용하여 그리드에서 값을 추출합니다.
    
    Args:
        grid (list): 전체 그리드 데이터
        pattern_positions (list): 패턴의 좌표 리스트 [(x1,y1), (x2,y2), ...]
    
    Returns:
        list: 패턴의 값 리스트 (예: ['B', 'P', 'B', 'B', 'P', 'B'])
    """
    values = []
    for x, y in pattern_positions:
        value = grid[x][y]
        if value:
            values.append(value.upper())
        else:
            values.append('')
    return values

def display_pattern_groups(zones):
    """
    패턴의 그룹 분석 결과를 별도 섹션에 표시합니다.
    """
    if not zones:
        return
    
    # 제목과 저장 버튼을 나란히 배치
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 패턴 그룹 분석")
    
    # 분석 결과를 저장할 리스트
    analysis_results = []
    
    # 모든 그룹에 대해 패턴 분석
    for zone in zones:
        patterns = get_pattern_positions()
        group_patterns = [p for p in patterns if p['columns'][0] >= zone['start_x'] and p['columns'][1] <= zone['end_x']]
        
        if len(group_patterns) < 4:  # 최소 4개의 패턴이 필요
            continue
            
        # 패턴 값 추출
        pattern_values = []
        for pattern in group_patterns[:4]:  # 처음 4개의 패턴만 사용
            values = []
            for x, y in pattern['coordinates']:
                relative_x = x - zone['start_x']
                value = zone['zone_data'][relative_x][y]
                if value:
                    values.append(value.upper())
            pattern_values.append(values)
            
        # 패턴 123과 1234의 그룹 검색
        groups_123 = []
        groups_1234 = []
        
        # 패턴 123 검색
        pattern_123_valid = True
        if len(pattern_values) >= 3:
            for i in range(3):
                if not pattern_values[i]:
                    pattern_123_valid = False
                    break
                group = find_pattern_group(pattern_values[i])
                if group is None:
                    pattern_123_valid = False
                    break
                groups_123.append(group)
        
        # 패턴 1234 검색
        pattern_1234_valid = True
        if len(pattern_values) >= 4:
            for i in range(4):
                if not pattern_values[i]:
                    pattern_1234_valid = False
                    break
                group = find_pattern_group(pattern_values[i])
                if group is None:
                    pattern_1234_valid = False
                    break
                groups_1234.append(group)
        
        # 결과 문자열 생성
        pattern_123_text = ''.join(groups_123) if pattern_123_valid and len(groups_123) == 3 else ''
        pattern_1234_text = ''.join(groups_1234) if pattern_1234_valid and len(groups_1234) == 4 else ''
        
        # 그룹 범위 텍스트
        group_range = f"{zone['start_x'] + 1}-{zone['end_x'] + 1}"
        
        # 분석 결과 저장
        if pattern_123_text or pattern_1234_text:
            analysis_results.append({
                'group_range': group_range,
                'pattern_123': pattern_123_text,
                'pattern_1234': pattern_1234_text
            })
        
        # 결과 표시
        st.markdown(f"#### 그룹 {group_range}")
        st.text(f"패턴 1,2,3 그룹: {pattern_123_text}")
        st.text(f"패턴 1,2,3,4 그룹: {pattern_1234_text}")
        st.markdown("---")
    
    # 저장 버튼 배치
    with col2:
        if st.button("모두 저장"):
            for result in analysis_results:
                save_pattern_record(
                    result['group_range'],
                    result['pattern_123'],
                    result['pattern_1234']
                )
            st.success("모든 패턴이 저장되었습니다!")

def get_pattern_statistics():
    """
    DB에서 패턴 통계를 계산합니다.
    """
    try:
        conn = sqlite3.connect('pattern_analysis.db')
        c = conn.cursor()
        
        # 전체 레코드 수 확인
        total_records = c.execute('SELECT COUNT(*) FROM pattern_records').fetchone()[0]
        
        # 현재 시간 기준 최근 3시간 타임스탬프 계산 (YYMMDDHH 형식)
        current_time = datetime.now()
        three_hours_ago = current_time - timedelta(hours=3)
        recent_timestamp = three_hours_ago.strftime("%y%m%d%H")
        
        if total_records <= 100:
            # 전체 레코드에 대한 통계
            r1_stats = c.execute('''
                SELECT pattern1 || result1 as p1r1, COUNT(*) as count
                FROM pattern_records
                WHERE result1 != ''
                GROUP BY p1r1
                ORDER BY count DESC
            ''').fetchall()
            
            r2_stats = c.execute('''
                SELECT pattern2 || result2 as p2r2, COUNT(*) as count
                FROM pattern_records
                WHERE result2 != ''
                GROUP BY p2r2
                ORDER BY count DESC
            ''').fetchall()
            
            sample_size = total_records
            
        else:
            # 최근 3시간 레코드 수 확인
            recent_count = c.execute(
                'SELECT COUNT(*) FROM pattern_records WHERE timestamp >= ?',
                (recent_timestamp,)
            ).fetchone()[0]
            
            # 최근 3시간과 최근 100개 중 큰 수로 결정
            if recent_count > 100:
                # 최근 3시간 데이터 사용
                r1_stats = c.execute('''
                    SELECT pattern1 || result1 as p1r1, COUNT(*) as count
                    FROM pattern_records
                    WHERE result1 != '' AND timestamp >= ?
                    GROUP BY p1r1
                    ORDER BY count DESC
                ''', (recent_timestamp,)).fetchall()
                
                r2_stats = c.execute('''
                    SELECT pattern2 || result2 as p2r2, COUNT(*) as count
                    FROM pattern_records
                    WHERE result2 != '' AND timestamp >= ?
                    GROUP BY p2r2
                    ORDER BY count DESC
                ''', (recent_timestamp,)).fetchall()
                
                sample_size = recent_count
                
            else:
                # 최근 100개 데이터 사용
                r1_stats = c.execute('''
                    SELECT pattern1 || result1 as p1r1, COUNT(*) as count
                    FROM pattern_records
                    WHERE result1 != ''
                    GROUP BY p1r1
                    ORDER BY count DESC
                    LIMIT 100
                ''').fetchall()
                
                r2_stats = c.execute('''
                    SELECT pattern2 || result2 as p2r2, COUNT(*) as count
                    FROM pattern_records
                    WHERE result2 != ''
                    GROUP BY p2r2
                    ORDER BY count DESC
                    LIMIT 100
                ''').fetchall()
                
                sample_size = 100

        # P1 패턴을 그룹화하고 정렬
        p1_groups = {
            'aa': [], 'ab': [], 'ba': [], 'bb': []
        }
        
        # P2 패턴을 그룹화하고 정렬
        p2_groups = {
            'bba': [], 'baa': [], 'abb': [], 'aab': [],
            'aba': [], 'aaa': [], 'bbb': [], 'bab': []
        }
        
        # 각 P1 패턴을 해당 그룹에 할당
        for pattern, count in r1_stats:
            if len(pattern) >= 2:
                group_key = pattern[:2].lower()
                if group_key in p1_groups:
                    p1_groups[group_key].append((pattern, count))

        # 각 P2 패턴을 해당 그룹에 할당
        for pattern, count in r2_stats:
            if len(pattern) >= 3:
                group_key = pattern[:3].lower()
                if group_key in p2_groups:
                    p2_groups[group_key].append((pattern, count))

        # P1 그룹의 최대 카운트를 계산
        p1_group_max_counts = {}
        for group, patterns in p1_groups.items():
            if patterns:
                p1_group_max_counts[group] = max(count for _, count in patterns)
            else:
                p1_group_max_counts[group] = 0

        # P2 그룹의 최대 카운트를 계산
        p2_group_max_counts = {}
        for group, patterns in p2_groups.items():
            if patterns:
                p2_group_max_counts[group] = max(count for _, count in patterns)
            else:
                p2_group_max_counts[group] = 0

        # 그룹들을 최대 카운트 기준으로 정렬
        sorted_p1_groups = sorted(p1_groups.items(), 
                                key=lambda x: p1_group_max_counts[x[0]], 
                                reverse=True)
        
        sorted_p2_groups = sorted(p2_groups.items(),
                                key=lambda x: p2_group_max_counts[x[0]],
                                reverse=True)

        conn.close()
        return {
            'total_records': total_records,
            'sample_size': sample_size,
            'p1_groups': sorted_p1_groups,
            'p2_groups': sorted_p2_groups
        }
        
    except Exception as e:
        st.error(f"통계 데이터 조회 중 오류 발생: {str(e)}")
        return None

def display_pattern_statistics(stats):
    """
    패턴 통계를 표시합니다.
    """
    if not stats:
        return

    # 기본 스타일 설정
    st.markdown("""
        <style>
        .stMarkdown {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 2em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 헤더 정보
    st.write("### 패턴 통계")
    st.write(f"전체 기록: {stats['total_records']}개 | 통계 표본: {stats['sample_size']}개")
    
    # 컬럼 생성
    col1, col2 = st.columns(2)
    
    # P1 Statistics
    with col1:
        st.write("#### P1 패턴 통계")
        for group_name, patterns in stats['p1_groups']:
            st.write(f"**{group_name.upper()} 그룹**")
            sorted_patterns = sorted(patterns, key=lambda x: x[1], reverse=True)
            group_total = sum(count for _, count in sorted_patterns)
            
            if group_total == 0:
                st.write("기록 없음 (0%)")
            else:
                for pattern, count in sorted_patterns:
                    group_percentage = (count / group_total) * 100
                    st.write(f"{pattern}: {count}회 ({group_percentage:.1f}%)")
            st.write("---")
    
    # P2 Statistics
    with col2:
        st.write("#### P2 패턴 통계")
        for group_name, patterns in stats['p2_groups']:
            st.write(f"**{group_name.upper()} 그룹**")
            sorted_patterns = sorted(patterns, key=lambda x: x[1], reverse=True)
            group_total = sum(count for _, count in sorted_patterns)
            
            if group_total == 0:
                st.write("기록 없음 (0%)")
            else:
                for pattern, count in sorted_patterns:
                    group_percentage = (count / group_total) * 100
                    st.write(f"{pattern}: {count}회 ({group_percentage:.1f}%)")
            st.write("---")

def main():
    # 페이지 전체 너비 설정
    st.set_page_config(layout="wide")
    
    st.title("Bead Road Parser")
    
    # Initialize session state
    if 'text_key' not in st.session_state:
        st.session_state.text_key = 0
    if 'grid' not in st.session_state:
        st.session_state.grid = None
    if 'show_grid' not in st.session_state:
        st.session_state.show_grid = False
    
    # 화면을 좌우로 분할 (비율 조정)
    left_col, right_col = st.columns([7, 3])
    
    # 왼쪽 컬럼: SVG 입력 및 분석 결과
    with left_col:
        svg_code = st.text_area("Paste SVG code here", height=200, key=f"svg_input_{st.session_state.text_key}")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Reset"):
                st.session_state.text_key += 1
                st.session_state.grid = None
                st.session_state.show_grid = False
                st.experimental_rerun()
        
        with col2:
            if st.button("Parse SVG"):
                if svg_code:
                    try:
                        grid = parse_bead_road_svg(svg_code)
                        st.session_state.grid = grid
                        st.session_state.show_grid = True
                        st.success("Successfully parsed the SVG code!")
                    except Exception as e:
                        st.error(f"Error parsing SVG: {str(e)}")
                else:
                    st.warning("Please paste SVG code first")
        
        # Display Full Grid if available
        if st.session_state.show_grid and st.session_state.grid is not None:
            st.subheader("Full Grid")
            display_grid(st.session_state.grid)
            
            # Process zones and display pattern analysis
            zones = divide_grid_into_overlapping_zones(st.session_state.grid)
            if zones:
                display_pattern_groups(zones)
            else:
                st.info("No zones with relevant data to display.")
    
    # 오른쪽 컬럼: 패턴 분석 기록
    with right_col:
        # 패턴 통계 표시
        stats = get_pattern_statistics()
        if stats:
            display_pattern_statistics(stats)
            st.markdown("---")  # 구분선 추가
        
        st.markdown("### 패턴 분석 기록")
        try:
            conn = sqlite3.connect('pattern_analysis.db')
            c = conn.cursor()
            records = c.execute('SELECT * FROM pattern_records ORDER BY round DESC LIMIT 10').fetchall()
            
            # 마지막 업데이트 시간 표시
            last_update = c.execute('SELECT MAX(timestamp) FROM pattern_records').fetchone()[0]
            if last_update:
                st.markdown(f"**마지막 업데이트:** {last_update[:2]}-{last_update[2:4]}-{last_update[4:6]} {last_update[6:8]}:{last_update[8:]}시")
            
            conn.close()
            
            if records:
                # Create a table header
                st.markdown("""
                | 라운드 | 시간 | 그룹 | P1 | R1 | P2 | R2 |
                |:------:|:----:|:----:|:--:|:--:|:--:|:--:|""")
                
                # Add each record to the table
                for record in records:
                    st.markdown(f"| {record[0]} | {record[1]} | {record[2]} | {record[3]} | {record[4]} | {record[5]} | {record[6]} |")
            else:
                st.info("저장된 기록이 없습니다.")
        except Exception as e:
            st.error(f"데이터 조회 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()