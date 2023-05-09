# from text_box_wrapper import wrap_with_ascii_art

# from colorama import Fore, Back, Style, init,deinit
# # from text_box_wrapper.wrapper import wrap,wrap_with_ascii_art
# import re
# import unicodedata
# from typing import Callable

# def wrap(min_padding=10, vertical_padding=None, border_string="#" * 5, alignment="center"):
#     def decorator(func: Callable) -> Callable:
#         def wrapper(*args, **kwargs):
#             text = func(*args, **kwargs)
#             return wrap_with_ascii_art(text, min_padding, vertical_padding, border_string, alignment)
#         return wrapper
#     return decorator

# def wrap_with_ascii_art(text, min_padding=10, vertical_padding=None, border_string="#" * 3, alignment="center") -> str:
#     def get_char_width(char):
#         width = unicodedata.east_asian_width(char)
#         return 2 if width in 'FWA' else 1

#     def get_text_width(text):
#         return sum(get_char_width(char) for char in text)
    
#     padding_char = " "
#     ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')  # 用于匹配ANSI转义序列的正则表达式
#     text_without_colors = ansi_escape.sub('', text)  # 移除彩色字符
#     text_lines = text.split("\n")
#     text_lines_without_colors = text_without_colors.split("\n")
    
#     max_line_length = max([get_text_width(line) for line in text_lines_without_colors])

#     # 如果未设置垂直填充，则根据边框字符串长度自动计算
#     if vertical_padding is None:
#         vertical_padding = len(border_string) // 2

#     # 计算外部边框的长度
#     border_length = max_line_length + min_padding * 2 + 2 * get_text_width(border_string)

#     # 构建上边框
#     top_border = border_string * (border_length // get_text_width(border_string))
#     top_border += border_string[:border_length % get_text_width(border_string)] + "\n"

#     # 构建下边框
#     bottom_border = border_string * (border_length // get_text_width(border_string))
#     bottom_border += border_string[:border_length % get_text_width(border_string)] + "\n"

#     # 构建垂直内边距行
#     vertical_padding_line = border_string + padding_char * (max_line_length + min_padding * 2) + border_string + "\n"

#     vertical_border_lines = max(int(len(border_string) / 2), 1)

#     # 处理文本的每一行，根据 alignment 参数添加左右填充
#     content_lines = []
#     for index, line in enumerate(text_lines):
#         total_padding = border_length - get_text_width(text_lines_without_colors[index]) - 2 * get_text_width(border_string)
        
#         if alignment == "left":
#             left_padding = 0
#             right_padding = total_padding
#         elif alignment == "right":
#             left_padding = total_padding
#             right_padding = 0
#         else:  # 默认为居中
#             left_padding = total_padding // 2
#             right_padding = total_padding - left_padding

#         content_line = border_string + padding_char * left_padding + line + padding_char * right_padding + border_string + "\n"
#         content_lines.append(content_line)

#     content = "".join(content_lines)

#     # 将各部分连接在一起，并在内容行之间添加垂直内边距
#     return (
#         top_border * vertical_border_lines +
#         vertical_padding_line * vertical_padding +
#         content +
#         vertical_padding_line * vertical_padding +
#         bottom_border * vertical_border_lines
#     )



# def wrap_with_ascii_art(text, min_padding=10, vertical_padding=None, border_string="#" * 5, alignment="center") -> str:
#     padding_char = " "
#     ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')  # 用于匹配ANSI转义序列的正则表达式
#     text_without_colors = ansi_escape.sub('', text)  # 移除彩色字符
#     text_lines = text.split("\n")
#     text_lines_without_colors = text_without_colors.split("\n")
    
#     max_line_length = max([len(line) for line in text_lines_without_colors])

#     # 如果未设置垂直填充，则根据边框字符串长度自动计算
#     if vertical_padding is None:
#         vertical_padding = len(border_string) // 2

#     # 计算外部边框的长度
#     border_length = max_line_length + min_padding * 2 + 2 * len(border_string)

#     # 构建上边框
#     top_border = border_string * (border_length // len(border_string))
#     top_border += border_string[:border_length % len(border_string)] + "\n"

#     # 构建下边框
#     bottom_border = border_string * (border_length // len(border_string))
#     bottom_border += border_string[:border_length % len(border_string)] + "\n"

#     # 构建垂直内边距行
#     vertical_padding_line = border_string + padding_char * (max_line_length + min_padding * 2) + border_string + "\n"

#     vertical_border_lines = max(int(len(border_string) / 2), 1)

#     # 处理文本的每一行，根据 alignment 参数添加左右填充
#     content_lines = []
#     for index, line in enumerate(text_lines):
#         total_padding = border_length - len(text_lines_without_colors[index]) - 2 * len(border_string)

#         if alignment == "left":
#             left_padding = 0
#             right_padding = total_padding
#         elif alignment == "right":
#             left_padding = total_padding
#             right_padding = 0
#         else:  # 默认为居中
#             left_padding = total_padding // 2
#             right_padding = total_padding - left_padding

#         content_line = border_string + padding_char * left_padding + line + padding_char * right_padding + border_string + "\n"
#         content_lines.append(content_line)

#     content = "".join(content_lines)

#     # 将各部分连接在一起，并在内容行之间添加垂直内边距
#     return (
#         top_border * vertical_border_lines +
#         vertical_padding_line * vertical_padding +
#         content +
#         vertical_padding_line * vertical_padding +
#         bottom_border * vertical_border_lines
#     )


 

from colorama import Fore, Back, Style, init,deinit
import re
import unicodedata
def wrap_with_ascii_art(text, min_padding=10, vertical_padding=None, border_string="#" * 5, alignment="center") -> str:
    def get_char_width(char):
        width = unicodedata.east_asian_width(char)
        return 2 if width in 'FWA' else 1

    def get_text_width(text):
        return sum(get_char_width(char) for char in text)
    
    padding_char = " "
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')  # 用于匹配ANSI转义序列的正则表达式
    text_without_colors = ansi_escape.sub('', text)  # 移除彩色字符
    text_lines = text.split("\n")
    text_lines_without_colors = text_without_colors.split("\n")
    
    max_line_length = max([get_text_width(line) for line in text_lines_without_colors])

    # 如果未设置垂直填充，则根据边框字符串长度自动计算
    if vertical_padding is None:
        vertical_padding = len(border_string) // 2

    # 计算外部边框的长度
    border_length = max_line_length + min_padding * 2 + 2 * get_text_width(border_string)

    # 构建上边框
    top_border = border_string * (border_length // get_text_width(border_string))
    top_border += border_string[:border_length % get_text_width(border_string)] + "\n"

    # 构建下边框
    bottom_border = border_string * (border_length // get_text_width(border_string))
    bottom_border += border_string[:border_length % get_text_width(border_string)] + "\n"

    # 构建垂直内边距行
    vertical_padding_line = border_string + padding_char * (max_line_length + min_padding * 2) + border_string + "\n"

    vertical_border_lines = max(int(len(border_string) / 2), 1)

    # 处理文本的每一行，根据 alignment 参数添加左右填充
    content_lines = []
    for index, line in enumerate(text_lines):
        total_padding = border_length - get_text_width(text_lines_without_colors[index]) - 2 * get_text_width(border_string)
        
        if alignment == "left":
            left_padding = 0
            right_padding = total_padding
        elif alignment == "right":
            left_padding = total_padding
            right_padding = 0
        else:  # 默认为居中
            left_padding = total_padding // 2
            right_padding = total_padding - left_padding

        content_line = border_string + padding_char * left_padding + line + padding_char * right_padding + border_string + "\n"
        content_lines.append(content_line)

    content = "".join(content_lines)

    # 将各部分连接在一起，并在内容行之间添加垂直内边距
    return (
        top_border * vertical_border_lines +
        vertical_padding_line * vertical_padding +
        'content' +
        vertical_padding_line * vertical_padding +
        bottom_border * vertical_border_lines
    )


# @wrap(min_padding=5, vertical_padding=2, border_string="###", alignment="center")
def banner():
  init()  # 初始化colorama
  green_circle = f"{Fore.GREEN}● success{Style.RESET_ALL}你好，成都"
  green_circle = f"{Fore.GREEN}● success{Style.RESET_ALL}asdas"
  # green_circle = f"{Fore.GREEN}● success{Style.RESET_ALL}"
  tag = 'uknoweee'
  message = f"{green_circle}\n Telegram keyword alert bot (Version: {tag})"
  return green_circle
  return '你好，成都'
  return message



print( wrap_with_ascii_art(banner()))


