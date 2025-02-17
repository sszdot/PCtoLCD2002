import tkinter as tk
from tkinter import filedialog
import os
import re

def get_file_content():
    """ 选择 txt 文件并读取内容 """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    file_path = filedialog.askopenfilename(title="选择一个字模文件", filetypes=[("Text files", "*.txt")])
    
    if not file_path:
        print("没有选择文件")
        return None, None
    
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
            return None, None
    
    return file_path, [line.strip() for line in file_content if line.strip()]

def parse_font_data(content):
    """ 解析多个 12x12 字模 """
    all_chars = []
    current_char = []
    width, height = 12, 12  # 固定 12x12

    for line in content:
        if line.startswith("DB"):
            parts = line.split(";")[0].strip().split()[1:]  # 过滤掉 DB 和后面的注释
            current_char.extend(parts)
        elif "*/" in line and current_char:  # 读取到注释，表示字符结束
            all_chars.append(current_char)
            current_char = []

    binary_matrices = []
    
    for hex_data in all_chars:
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
        
        binary_matrices.append(binary_matrix)

    return binary_matrices

def generate_svg(binary_matrices, file_path):
    """ 生成 SVG 文件 """
    cell_size = 10  # 每个点的大小
    char_width = 12
    char_height = 12
    total_width = len(binary_matrices) * char_width
    total_height = char_height

    svg_elements = []
    
    for char_index, binary_matrix in enumerate(binary_matrices):
        x_offset = char_index * char_width * cell_size  # 每个字符向右排列
        
        for row, line in enumerate(binary_matrix):
            for col, bit in enumerate(line):
                if bit == '1':  # 如果是1，绘制黑色像素
                    x = x_offset + col * cell_size
                    y = row * cell_size
                    svg_elements.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="black"/>')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width * cell_size}" height="{total_height * cell_size}">
{''.join(svg_elements)}
</svg>'''

    svg_filename = os.path.splitext(file_path)[0] + ".svg"
    with open(svg_filename, "w", encoding="utf-8") as svg_file:
        svg_file.write(svg_content)
    
    print(f"SVG 文件已生成: {svg_filename}")

def main():
    file_path, content = get_file_content()
    if content:
        binary_matrices = parse_font_data(content)
        generate_svg(binary_matrices, file_path)

if __name__ == "__main__":
    main()