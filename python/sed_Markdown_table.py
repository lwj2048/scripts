#修改markdown中的表格，每次新数据插入一列。表格如下面所示
# |name|name2|
# |----|----|
# |num1|123|
# |num2|456|
# |num3|879|

def update_markdown_table(name,value1,value2,value3):
    markdown_file = "md_file.md"  # 替换为实际的Markdown文件路径
    table_name = "name"  # 表格的标题
    with open(markdown_file, "r") as f:
        lines = f.readlines()
    new_lines = []
    in_table = False

    for line in lines:
        line = line.strip()
        print(line)
        if line.startswith("|" + table_name + "|"):
            print("================ ")
            new_line = line + name + "|"
            new_lines.append(new_line)
            in_table = True
        elif in_table and line.startswith("|----"):
            new_line = line + "----|"
            new_lines.append(new_line)
        elif in_table and line.startswith("|num1|"):
            new_line = line + str(value1) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("|num2|"):
            new_line = line + str(value2) + '|'
            new_lines.append(new_line)
        elif in_table and line.startswith("|num3|"):
            new_line = line + str(value3) + '|'
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open(markdown_file, "w") as f:
        f.write("\n".join(new_lines))

if __name__ == "__main__":
    update_markdown_table("name2", "123", "456","879")
    print("Markdown table updated successfully!")
