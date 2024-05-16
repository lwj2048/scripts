# {{ report1.title }}

## 简介

{{ report1.introduction }}

## 数据

| 测试项 | {% for env in report1.environments %} {{ env }} |{% endfor %}
|--------|{% for _ in report1.environments %}------|{% endfor %}
{% for test_name, values in report1.data.items() %}
| {{ test_name }} | {% for value in values %} {{ value }} |{% endfor %}
{% endfor %}

## 结论

{{ report1.conclusion }}

---

# {{ report2.title }}

## 简介

{{ report2.introduction }}

## 数据

| 测试项 | {% for env in report2.data.keys() %} {{ env }} |{% endfor %}
|--------|{% for _ in report2.data.keys() %}------|{% endfor %}
{% for idx, test in enumerate(report2.test_class) %}
| {{ test }} | {% for env, results in report2.data.items() %} {{ results[idx] }} |{% endfor %}
{% endfor %}

## 结论

{{ report2.conclusion }}
