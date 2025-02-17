import tkinter as tk
from tkinter import filedialog
import os
import re

def get_file_content():
    """ 打开 Windows 资源管理器选择 txt 文件，并读取文件内容 """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    file_path = filedialog.askopenfilename(title="选择一个字模文件", filetypes=[("Text files", "*.txt")])
    
    if not file_path:
        print("没有选择文件")
        return None, None, None
    
    print(f"你选择的文件是: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='GBK') as file:
                file_content = file.readlines()
        except UnicodeDecodeError:
            print("无法读取文件，请检查文件编码")
            return None, None, None
    
    # 解析文件内容，找出图像宽度和高度
    width, height = 0, 0
    for line in file_content:
        match = re.search(r"/\*\s*\((\d+)\s*X\s*(\d+)\s*\)\s*\*/", line)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            break  # 找到尺寸后退出
    
    return file_path, [line.strip() for line in file_content if line.strip()], (width, height)

def parse_font_data(content, width, height):
    """ 解析 txt 文件中的点阵数据 """
    hex_data = []
    
    for line in content:
        if line.startswith("DB"):
            parts = line.split(";")[0].strip().split()[1:]  # 过滤掉 DB 和后面的注释
            hex_data.extend(parts)  # 添加到 hex_data
    
    # 转换十六进制数据
    binary_data = []
    for hex_value in hex_data:
        binary_string = bin(int(hex_value[:-1], 16))[2:].zfill(8)  # 去掉 H，转换为二进制，并补足 8 位
        binary_string = binary_string[::-1]  # 低位在前，所以需要反转
        binary_data.append(binary_string)
    
    # 按行重组数据
    binary_matrix = []
    bytes_per_row = width // 8 + (1 if width % 8 else 0)  # 计算每行有多少个字节
    
    for i in range(height):
        row_data = "".join(binary_data[i * bytes_per_row:(i + 1) * bytes_per_row])
        row_data = row_data[:width]  # 只取有效的宽度
        binary_matrix.append(row_data)
    
    return binary_matrix

def generate_svg(binary_matrix, file_path):
    """ 生成 SVG 文件 """
    cell_size = 10  # 每个点的大小
    width = len(binary_matrix[0])  # 取第一行的宽度
    height = len(binary_matrix)  # 高度
    
    svg_elements = []
    
    for row, line in enumerate(binary_matrix):
        for col, bit in enumerate(line):
            if bit == '1':  # 如果是1，绘制黑色像素
                x = col * cell_size
                y = row * cell_size
                svg_elements.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="black"/>')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width * cell_size}" height="{height * cell_size}">
{''.join(svg_elements)}
</svg>'''

    svg_filename = os.path.splitext(file_path)[0] + ".svg"
    with open(svg_filename, "w", encoding="utf-8") as svg_file:
        svg_file.write(svg_content)
    
    print(f"SVG 文件已生成: {svg_filename}")

def main():
    file_path, content, (width, height) = get_file_content()
    if content and width and height:
        binary_matrix = parse_font_data(content, width, height)
        generate_svg(binary_matrix, file_path)

if __name__ == "__main__":
    main()
