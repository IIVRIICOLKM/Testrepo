import re
import pandas as pd
import copy
from pathlib import Path

class FA:
    def __init__(self, state_set:set, start_set:set, delta_functions:pd.DataFrame, final_state_set:set, terminal_set:set):
        self.state_set = state_set
        self.start_set = start_set
        self.delta_functions = delta_functions
        self.final_state_set = final_state_set
        self.terminal_set = terminal_set
        self.fa_type = 'EPS-NFA' if 'ε' in self.delta_functions.columns else 'NFA'

        # 초기 입력 DFA 식별
        cnt = 0
        for state in sorted(list(self.state_set)):
            for symbol in sorted(list(self.terminal_set)):
                if state in self.delta_functions.index and self.delta_functions.loc[state, symbol] != None and len(self.delta_functions.loc[state, symbol]) != 1:
                    cnt += 1
        # DFA 조건 만족 시, 치환 진행
        if self.fa_type != 'EPS-NFA' and cnt == 0:
            states = []
            for state in sorted(self.state_set):
                states.append({state})

            indexs = ['A'] * len(states)

            for i in range(len(states)):
                alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                indexs[i] = alpha[i]

            self.delta_functions.index = indexs
            self.replace_dfa(states)
            self.fa_type = 'DFA'

    def show_states_information(self):
        print(f'----------------- 매핑 함수 -----------------')
        print(self.delta_functions)
        print(f'--------------------------------------------')
        print(f'현재 상태 집합 : {sorted(self.state_set)}')
        print(f'현재 시작 상태 : {sorted(self.start_set)}')
        print(f'현재 종결 상태 : {sorted(self.final_state_set)}', end='\n\n')

    def nfa_to_dfa(self):
        # 조기 종료
        if self.fa_type != 'NFA' and self.fa_type != 'EPS-NFA':
            print(f'현재 타입은 {self.fa_type}입니다.', end='\n\n')
            return
        # 딕셔너리 테이블 칼럼(터미널 심볼) 초기화
        df_dict = {}
        for i in range(len(self.terminal_set)):
            df_dict[sorted(list(self.terminal_set))[i]] = []

        # 시작 상태에 대한 ε-Closure 연산
        if self.fa_type == 'EPS-NFA':
            cnt = 0
            while True:
                idx = sorted(list(self.start_set))[cnt]
                if (idx in self.delta_functions.index and self.delta_functions.loc[idx, 'ε'] != None):
                    add_set = self.delta_functions.loc[idx, 'ε']
                    self.start_set = self.start_set.union(add_set) if add_set is not None else self.start_set
                cnt += 1
                if cnt == len(self.start_set):
                    break
        
        # 상태 확장 및 데이터프레임 생성
        transferable_states = []
        transferable_states.append(self.start_set)
        self.extend_state(df_dict, transferable_states)
        self.delta_functions = pd.DataFrame(df_dict)

        self.delta_functions.index = transferable_states
        print(self.delta_functions, end='\n\n')
        # 데이터프레임 인덱스 치환
        indexs = ['A'] * len(transferable_states)
        for i in range(len(transferable_states)):
            alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            indexs[i] = alpha[i]
        self.delta_functions.index = indexs

        # 데이터 프레임 전체 치환 및 타입 변경
        self.replace_dfa(transferable_states)

        self.show_states_information()
        self.fa_type = 'DFA'

    def state_distribution(self, dist_sets:list, processing_idx:int) -> list:
        # State Matrix 생성 및 초기화
        state_mat = []
        dist_size = len(dist_sets)
        dist_set_size = len(dist_sets[processing_idx])

        for i in range(dist_set_size):
            state_mat.append([])

        # 상태 넘버링
        for i in range(dist_set_size):
            for j in range(len(self.terminal_set)):
                symbol = sorted(self.terminal_set)[j]
                current = self.delta_functions.loc[dist_sets[processing_idx][i], symbol]
                for k in range(dist_size):
                    if current in dist_sets[k]:
                        state_mat[i].append(k)
                    elif k == dist_size - 1:
                        state_mat[i].append(-1)
                # 마지막에 문자 추가
                if j == len(self.terminal_set) - 1:
                    state_mat[i].append(dist_sets[processing_idx][i])
        # State Matrix : ex) [[0, 0, 'A'], [0, 1, 'B'], [0, 1, 'D']]

        # 종결 상태와 시작 상태가 동일한경우 빈 리스트 반환
        if len(state_mat) == 0:
            return state_mat
        
        state_mat = sorted(state_mat)
        ptr = 0
        d_list = [[state_mat[ptr].pop()]]

        # 집합 분해 후 결괏값 반환
        for i in range(1, len(state_mat)):
            current = state_mat[i].pop()
            # 문자 제거 후 일치 여부 비교
            if state_mat[i - 1] == state_mat[i]:
                d_list[ptr].append(current)
            else:
                d_list.append([])
                ptr += 1
                d_list[ptr].append(current)

        return d_list

    def dfa_to_rdfa(self):
        if self.fa_type != 'DFA':
            print(f'현재 타입은 {self.fa_type}입니다.')
            return
        
        # 종결, 비종결 상태 분해
        unfinal_state_set = self.state_set - self.final_state_set
        d_lists = [sorted(unfinal_state_set), sorted(self.final_state_set)]

        while True:
            updated_d_lists = []
            distributable_checks = []
            dists_size = len(d_lists)
            # 부분집합별 상태 검사
            for i in range(dists_size):
                updated_d_list = self.state_distribution(d_lists, i)
                distributable_checks.append(len(updated_d_list) > 1)
                updated_d_lists += updated_d_list

            d_lists = updated_d_lists
            if not sum(distributable_checks):
                break
        
        df_dict = {}
        for i in range(len(self.terminal_set)):
            df_dict[sorted(self.terminal_set)[i]] = []

        # 재결합 후 델타펑션 리뉴얼
        dists_size = len(d_lists)
        for i in range(dists_size):
            for symbol in sorted(self.terminal_set):
                for k in range(dists_size):
                    current = self.delta_functions.loc[sorted(d_lists)[i][0], symbol]
                    if not current:
                        df_dict[symbol].append(None)
                        break
                    if current in d_lists[k]:
                        df_dict[symbol].append(set(d_lists[k]))
        self.delta_functions = pd.DataFrame(df_dict)

        # 인덱스 치환
        for i in range(dists_size):
            d_lists[i] = set(d_lists[i])
        indexs = ['A'] * len(d_lists)
        for i in range(dists_size):
            alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            indexs[i] = alpha[i]
        self.delta_functions.index = indexs
        # DFA 치환 및 타입 변경
        self.replace_dfa(d_lists)
        self.show_states_information()
        self.fa_type = 'RDFA'

    def extend_state(self, df_dict:dict, transferable_states:list):
        cnt = 0
        while True:
            # delta_states : 현재까지 탐색된 전이 가능 상태
            delta_states = list(transferable_states[cnt])
            # 심볼 단위 탐색
            for symbol in sorted(list(self.terminal_set)):
                extended_state_set = set()
                # delta_states 리스트 내의 상태 집합의 구성 원소
                for delta_state in delta_states:
                    # 원자 상태의 심볼 조회 시 이동 가능 상태 파악 
                    searcing_state_set = self.delta_functions.loc[delta_state, symbol] \
                        if delta_state in self.delta_functions.index \
                        else None
                    # 공집합 제외
                    if searcing_state_set != None:
                        # ε-Closure 연산
                        if self.fa_type == 'EPS-NFA':
                            cnt_inner = 0
                            while True:
                                print(searcing_state_set)
                                idx = list(searcing_state_set)[cnt_inner]
                                print(idx)
                                if idx in self.delta_functions.index and self.delta_functions.loc[idx, 'ε'] != None:
                                    searcing_state_set = searcing_state_set.union(self.delta_functions.loc[idx, 'ε'])
                                cnt_inner += 1

                                if len(searcing_state_set) == cnt_inner:
                                    break
                        # 조회된 이동 가능 상태를 확장
                        extended_state_set = extended_state_set.union(searcing_state_set)
                # 딕셔너리에 확장된 원소 상태 삽입
                if len(extended_state_set) != 0:
                    df_dict[symbol].append(extended_state_set) 
                    if extended_state_set not in transferable_states:
                        transferable_states.append(extended_state_set)
                else: 
                    df_dict[symbol].append(None)

            # 반복 종료 : 전이 가능 상태 다 탐색
            cnt += 1
            if cnt == len(transferable_states):
                break

    def replace_dfa(self, transferable_states:list):
        alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        # DFA는 이미 알파벳으로 치환된 상태이기 때문에 기존 상태집합 정렬
        if self.fa_type == 'DFA':
            for i in range(len(transferable_states)):
                transferable_states[i] = list(transferable_states[i])

            transferable_states = sorted(transferable_states)

            for i in range(len(transferable_states)):
                transferable_states[i] = frozenset(transferable_states[i])

        # 시작, 종결 상태 초기화
        self.state_set.clear()
        tmp = copy.deepcopy(self.final_state_set)
        self.final_state_set.clear()

        # 시작 상태를 A로 설정
        self.start_set = {'A'}
        self.state_set = self.state_set.union(self.start_set)

        # 시작 상태, 종결 상태 탐색 및 치환
        for index in self.delta_functions.index:
            for symbol in self.terminal_set:
                for i in range(len(transferable_states)):
                    # 종결 상태에 대한 치환
                    for j in range(len(tmp)):
                        if list(tmp)[j] in transferable_states[i]:
                            self.final_state_set = self.final_state_set.union({alpha[i]})
                    # 상태 알파벳 치환 및 상태집합 재구성
                    if self.delta_functions.loc[index, symbol] == transferable_states[i]:
                        self.delta_functions.loc[index, symbol] = alpha[i]
                        self.state_set = self.state_set.union({alpha[i]})

# (information_dict, delta_functions)
def preprocess(filename:str)->tuple:

    DELTA_TEXT_PATTERN = r'Delta[A-Za-zε0-9(){}=,\n]+}\n?}'
    DELTA_ELEMENT_PATTERN = r'[(][q0-90-90-9]+,[a-z0-9ε][)]={[q0-90-90-9,]+}'
    STATE_INFOS_PATTERN = r'[A-Za-z]+=\{(?:q\d{3},?)+\}'
    TERMINAL_PATTERN = r'[A-Za-z]+=\{(?:\s*(?:\d+|[A-Za-z])\s*(?:,\s*(?:\d+|[A-Za-z])\s*)*)\}'
    EQUAL_PATTERN = r'[a-zA-Z]+='

    with open(filename, 'r', encoding='utf-8') as f:
        raw_text = ''.join(f.readlines())
        raw_text = re.sub(
            ' ', 
            '', 
            re.sub(r'\n+', '\n', raw_text)
            )
        inform_text = re.sub(DELTA_TEXT_PATTERN, '', raw_text)
        delta_text = ''.join(re.findall(DELTA_TEXT_PATTERN, raw_text))

        # 상태, 터미널 전처리
        informs_set_list = re.findall(STATE_INFOS_PATTERN, inform_text)
        # ex) ['TerminalSet={a,b,c,d, ...}']
        terminal_set_list = re.findall(TERMINAL_PATTERN, inform_text)
        terminal_set_text = terminal_set_list[0]
        informs_set_list.append(terminal_set_text)
        inform_dict = {}

        for informs_set in informs_set_list:
            equal_idx = re.search(EQUAL_PATTERN, informs_set).end() - 1
            
            key = informs_set[:equal_idx]
            value = set(
                    informs_set[equal_idx + 1:]
                        .replace('{', '')
                        .replace('}', '')
                        .split(',')
                )
            inform_dict[key] = value

        # 데이터프레임 삽입용 딕셔너리 생성
        df_dict = {}
        equal_idx = re.search(EQUAL_PATTERN, terminal_set_text).end() - 1
        terminal_symbols_list = terminal_set_text[equal_idx+1:].split(',')
        terminal_symbols_list.append('ε')

        # ex) df_dict = {'a': [], 'b': [], 'c': [], 'd': [], 'ε': []}
        for i in range(len(terminal_symbols_list)):
            terminal_symbols_list[i] = terminal_symbols_list[i].replace('{', '').replace('}', '')
            df_dict[terminal_symbols_list[i]] = []
        
        # 델타 함수 데이터 전처리
        # ex) ['(q000,a)={q000,q001}', '(q000,b)={q000,q002}', '(q001,a)={q001,q002}', '(q001,ε)={q000,q001}', ...] 정렬 확정 플래그

        deltafunc_text_list = sorted(re.findall(DELTA_ELEMENT_PATTERN, delta_text))
        transferable_states = []

        for deltafunc_text in deltafunc_text_list:
            equal_idx = re.search(r'[a-zA-Z0-9ε,()]+=', deltafunc_text).end() - 1
            left_side = deltafunc_text[:equal_idx].split(',')
            right_side = deltafunc_text[equal_idx + 1:].split(',')
            state = ''.join(left_side[0]).replace('(', '')
            if len(transferable_states) == 0:
                transferable_states.append(state)
            symbol = ''.join(left_side[1]).replace(')', '')
            
            for i in range(len(right_side)):
                right_side[i] = right_side[i].replace('{', '').replace('}', '')
            state_set = set(right_side)

            # 이동 가능 상태 리스트에 현재 진행중인 state 포함된 경우
            if state not in transferable_states:
                for i in range(len(terminal_symbols_list)):
                    if len(df_dict[terminal_symbols_list[i]]) != len(transferable_states):
                        df_dict[terminal_symbols_list[i]].append(None)
                transferable_states.append(state)

            df_dict[symbol].append(state_set)
        
        for i in range(len(terminal_symbols_list)):
            if len(df_dict[terminal_symbols_list[i]]) != len(transferable_states):
                df_dict[terminal_symbols_list[i]].append(None)

        df = pd.DataFrame(df_dict)
        df.index = transferable_states
        
        # df 처리 후 입실론 전이가 없는 경우 -> 입실론 칼럼 제거
        if df['ε'].isnull().sum() == len(df):
            df = df.drop(columns='ε')

        return inform_dict, df

if __name__ == '__main__':

    for p in Path('inputs').iterdir():
        print(f'-----------------------------------------------------------------------------------------------------', end='\n\n')
        inform_dict, delta_functions = preprocess(p)

        fa_test = FA(inform_dict['StateSet'], inform_dict['StartState'], delta_functions, inform_dict['FinalStateSet'], inform_dict['TerminalSet'])

        print(f'---------- 입력 {p} NFA -> DFA 변환 결과 ----------', end='\n\n')
        fa_test.nfa_to_dfa()
        print(f'------------------------------------------------------------------', end='\n\n')
        print(f'---------- 입력 {p} DFA -> RDFA 변환 결과 ----------', end='\n\n')
        fa_test.dfa_to_rdfa()
        print(f'------------------------------------------------------------------', end='\n\n')