import re
import pandas as pd
import copy

class FA:
    def __init__(self, state_set:set, start_set:set, delta_functions:pd.DataFrame, final_state_set:set, terminal_set:set):
        self.state_set = state_set
        self.start_set = start_set
        self.delta_functions = delta_functions
        self.final_state_set = final_state_set
        self.terminal_set = terminal_set

        self.fa_type = 'EPS-NFA' if 'ε' in self.delta_functions.columns else 'NFA'

        cnt = 0
        for state in sorted(list(self.state_set)):
            for symbol in sorted(list(self.terminal_set)):
                if state in self.delta_functions.index and self.delta_functions.loc[state, symbol] != None and len(self.delta_functions.loc[state, symbol]) != 1:
                    cnt += 1
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

    def nfa_to_dfa(self):
        if self.fa_type != 'NFA' and self.fa_type != 'EPS-NFA':
            print(f'현재 타입은 {self.fa_type}입니다.')
            return
        df_dict = {}
        for i in range(len(self.terminal_set)):
            df_dict[sorted(list(self.terminal_set))[i]] = []

        transferable_states = []

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

        transferable_states.append(self.start_set)
        self.extend_state(df_dict, transferable_states)
        # 데이터프레임 변경 및 인덱스 설정
        self.delta_functions = pd.DataFrame(df_dict)
        self.delta_functions.index = transferable_states
        indexs = ['A'] * len(transferable_states)

        for i in range(len(transferable_states)):
            alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            indexs[i] = alpha[i]

        self.delta_functions.index = indexs
        
        # 치환
        self.replace_dfa(transferable_states)
        self.fa_type = 'DFA'

        
    def dfa_to_rdfa(self):
        if self.fa_type != 'DFA':
            print(f'현재 타입은 {self.fa_type}입니다.')
            return
        
        unfinal_state_set = self.state_set - self.final_state_set
        distributes = [sorted(unfinal_state_set), sorted(self.final_state_set)]

        unf_mat = []
        f_mat = []

        for i in range(len(distributes[0])):
            unf_mat.append([])

        for i in range(len(distributes[1])):
            f_mat.append([])

        for i in range(len(distributes[0])):
            for j in range(len(self.terminal_set)):
                symbol = sorted(self.terminal_set)[j]
                current = self.delta_functions.loc[distributes[0][i], symbol]
                if current in distributes[0]:
                    unf_mat[i].append(0)
                elif current in distributes[1]:
                    unf_mat[i].append(1)
                else:
                    unf_mat[i].append(None)

                if j == len(self.terminal_set) - 1:
                    unf_mat[i].append(distributes[0][i])

        for i in range(len(distributes[1])):
            for j in range(len(self.terminal_set)):
                symbol = sorted(self.terminal_set)[j]
                current = self.delta_functions.loc[distributes[1][i], symbol]
                if current in distributes[0]:
                    f_mat[i].append(0)
                elif current in distributes[1]:
                    f_mat[i].append(1)
                else:
                    f_mat[i].append(None)

                if j == len(self.terminal_set) - 1:
                    f_mat[i].append(distributes[1][i])
        
        ptr = 0
        d_list = [[unf_mat[ptr].pop()]]

        for i in range(1, len(unf_mat)):
            current = unf_mat[i].pop()
            if unf_mat[i - 1] == unf_mat[i]:
                d_list[ptr].append(current)
            else:
                d_list.append([])
                ptr += 1
                d_list[ptr].append(current)

            if i == len(unf_mat) - 1:
                ptr = 0

        d1_list = [[f_mat[ptr].pop()]]

        for i in range(1, len(f_mat)):
            current = f_mat[i].pop()
            if f_mat[i - 1] == f_mat[i]:
                d1_list[ptr].append(current)
            else:
                d1_list.append([])
                ptr += 1
                d1_list[ptr].append(current)
        
        for i in range(len(d1_list)):
            d_list.append(d1_list[i])

        df_dict = {}
        for i in range(len(self.terminal_set)):
            df_dict[sorted(self.terminal_set)[i]] = []

        for i in range(len(d_list)):
            for symbol in sorted(self.terminal_set):
                for k in range(len(d_list)):
                    current = self.delta_functions.loc[sorted(d_list)[i][0], symbol]
                    if not current:
                        df_dict[symbol].append(None)
                        break
                    if current in d_list[k]:
                        df_dict[symbol].append(set(d_list[k]))

        print(df_dict)
        self.delta_functions = pd.DataFrame(df_dict)
        print(self.delta_functions)
        for i in range(len(d_list)):
            d_list[i] = set(d_list[i])

        self.delta_functions.index = d_list
        indexs = ['A'] * len(d_list)

        for i in range(len(d_list)):
            alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            indexs[i] = alpha[i]

        self.delta_functions.index = indexs
        
        # 치환
        self.replace_dfa(d_list)
        print(self.delta_functions)
        self.fa_type == 'RDFA'

    def extend_state(self, df_dict:dict, transferable_states:list):
        cnt = 0
        while True:
            delta_states = list(transferable_states[cnt])
            for symbol in sorted(list(self.terminal_set)):
                extended_state_set = set()
                for delta_state in delta_states:
                    searcing_state_set = self.delta_functions.loc[delta_state, symbol] \
                        if delta_state in self.delta_functions.index \
                        else None
            
                    if searcing_state_set != None:
                        if self.fa_type == 'EPS-NFA':
                            cnt_inner = 0
                            while True:
                                idx = sorted(list(searcing_state_set))[cnt_inner]

                                if idx in self.delta_functions.index and self.delta_functions.loc[idx, 'ε'] != None:
                                    searcing_state_set = searcing_state_set.union(self.delta_functions.loc[idx, 'ε'])
                                cnt_inner += 1

                                if len(searcing_state_set) == cnt_inner:
                                    break
                                      
                        extended_state_set = extended_state_set.union(searcing_state_set)

                if len(extended_state_set) != 0:
                    df_dict[symbol].append(extended_state_set) 
                    if extended_state_set not in transferable_states:
                        transferable_states.append(extended_state_set)
                else: 
                    df_dict[symbol].append(None)

            cnt += 1
            if cnt == len(transferable_states):
                break

    def replace_dfa(self, transferable_states:list):
        alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        self.state_set.clear()
        tmp = copy.deepcopy(self.final_state_set)
        self.final_state_set.clear()
        self.start_set = {'A'}
        self.state_set = self.state_set.union(self.start_set)

        for index in self.delta_functions.index:
            for symbol in self.terminal_set:
                for i in range(len(transferable_states)):
                    for j in range(len(tmp)):
                        if list(tmp)[j] in transferable_states[i]:
                            self.final_state_set = self.final_state_set.union({alpha[i]})

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

inform_dict, delta_functions = preprocess('input_dfa.txt')

fa_test = FA(inform_dict['StateSet'], inform_dict['StartState'], delta_functions, inform_dict['FinalStateSet'], inform_dict['TerminalSet'])
fa_test.nfa_to_dfa()
fa_test.dfa_to_rdfa()