# import numpy as np
# import pandas as pd

# friend_list = {
#     "name": ["John", "Jenny", "Nate"],
#     "midterm": [95, 85, 85],
#     "final": [90, 90, 70],
# }
# df = pd.DataFrame(friend_list)
# df2 = pd.DataFrame([["Ben", {1, 2}, {3, 4}]], columns=["name", "midterm", "final"])

# new_df = pd.concat([df, df2])

# new_df.index=["sex", "fuck", "you", "shit"]

# print("sex" in new_df.index)

# test_li = ['abc' * 100]

# print(new_df[0:1]['midterm'].values)
# import pandas as pd

# testdict = {"a":[{"q000", "q001"}, {"q001", "q002"}],
#             "b":[{"q000", "q002"}, None],
#             "ε":[None, {"q000", "q001"}]}
# df = pd.DataFrame(testdict)
# df.index=["q000","q001"]
# print(df[1:2])

# import pandas as pd

# testdict = {'a':[{"q000", "q001"}, {"q001", "q002"}],
#             'b':[{"q000", "q002"}, None],
#             'c':[None, {"q000", "q001"}]}
# df = pd.DataFrame(testdict)
# df.index=[{"a", "b"},{"c", "d"}]
# index Can be Set!!
# print(df)

# import re

# pat = r'\{(?:\s*(?:\d+|[A-Za-z])\s*(?:,\s*(?:\d+|[A-Za-z])\s*)*)\}'

# print(re.findall(pat, '{1, 2, 3, 4}'))
# print(re.findall(pat, '{q000,q001,q002,q003,q004}'))
# print(re.findall(pat, '{a, b, c, d}'


# print(sorted([[1, 1, 'A'], [2, 1, 'B'], [2, 2, 'C'], [1, 1, 'D'], [1, 2, 'E'], [2, 1, 'F']]))

# import pandas as pd

# testdict = {'a':[['B', 'D'], ['B', 'D'], ['B', 'D']],
#             'b':[['B', 'D'], ['C', 'E'], ['C', 'E']]}
# df = pd.DataFrame(testdict)

# df.index = ({'A'}, {'B', 'D'}, {'C', 'E'})
# print(df)

# from pathlib import Path

# for p in Path('inputs').iterdir():
#    print(p)
#    print(sorted([]))

#    with open(p, 'r', encoding='utf-8') as f:
#        print('success')

# print(sorted([['A'], ['C'], ['B'], ['D', 'E']]))

# zerochecker = [False, False, False]
# if not sum(zerochecker):
#     print('all 0')
# else:
#     print('not all 0')

temp = [['B'], ['A'], ['C']]
print(temp[0] > temp[1])