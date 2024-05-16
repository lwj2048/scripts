from jinja2 import Environment, FileSystemLoader
import os

# 设置模板文件夹
template_dir = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(template_dir))

# 注册 enumerate 函数到 Jinja2 环境
env.globals.update(enumerate=enumerate)

# 加载模板
template = env.get_template('report_template.md')

# 定义第一个数据集
data1 = {
    'title': '测试报告',
    'introduction': '这是一个自动生成的测试报告。',
    'environments': ['env1', 'env2', 'env3'],
    'data': {
        '测试项1': ['通过', '失败', '通过'],
        '测试项2': ['失败', '失败', '通过'],
        '测试项3': ['通过', '通过', '失败']
    },
    'conclusion': '测试报告结束。'
}

# 定义第二个数据集
data2 = {
    'title': '测试报告2',
    'introduction': '这是一个自动生成的测试报告。',
    'test_class': ['测试项1', '测试项2', '测试项3'],
    'data': {
        'env1': ['通过', '失败', '通过'],
        'env2': ['失败', '失败', '通过'],
        'env3': ['通过', '通过', '失败']
    },
    'conclusion': '测试报告结束。'
}

# 渲染模板
report_content = template.render(report1=data1, report2=data2)

# 将渲染结果写入文件
with open('report.md', 'w', encoding='utf-8') as f:
    f.write(report_content)

print("报告生成成功：report.md")
