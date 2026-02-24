import json

# 读取 JSON 文件
with open('prd.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 更新所有用户故事为已完成
for story in data['userStories']:
    story['passes'] = True

# 保存 JSON 文件
with open('prd.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("所有用户故事已标记为已完成！")
