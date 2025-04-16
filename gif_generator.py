from PIL import Image, ImageDraw, ImageFont
import emoji

# 定義要展示的文字（包含多行）
text = ("Hi there 👋\n"
        "I'm Darrius, a software engineer\n"
        "passionate about AI & Cybersecurity.\n"
        "Welcome to my GitHub!")

# 使用 FiraCode 字體
try:
    base_font = ImageFont.truetype(
        "./asset/Fira_Code/static/FiraCode-Medium.ttf", 
        size=32,
    )
except IOError:
    base_font = ImageFont.load_default()

# 用來渲染 emoji 的字型，使用較大的尺寸以確保清晰度
try:
    emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", size=32)  # 調大 emoji 尺寸
except IOError:
    emoji_font = base_font

# 設定一些畫布配置參數
padding = 20      # 圖片邊界空白
line_spacing = 7  # 行間距

def is_emoji(char):
    """檢查字符是否為 emoji"""
    return char in emoji.EMOJI_DATA

def draw_text_with_emoji(draw, text, x, y, base_font, emoji_font, show_cursor=False):
    """使用不同的字體來繪製文字和emoji"""
    cursor_x = x
    for char in text:
        if is_emoji(char):
            # 為 emoji 創建一個新的臨時圖像以保持顏色
            emoji_img = Image.new('RGBA', (50, 50), (255, 255, 255, 0))  # 透明背景
            emoji_draw = ImageDraw.Draw(emoji_img)
            emoji_draw.text((0, 0), char, font=emoji_font, embedded_color=True)
            # 獲取 emoji 的實際邊界框
            bbox = emoji_img.getbbox()
            if bbox:
                emoji_img = emoji_img.crop(bbox)
                # 計算垂直位置以對齊文字
                text_height = base_font.getbbox("X")[3]  # 使用大寫X作為參考高度
                emoji_y = int(y + (text_height - emoji_img.height) // 2)  # 轉換為整數
                # 貼上 emoji
                img = draw._image  # 獲取底層圖像
                img.paste(emoji_img, (int(cursor_x), emoji_y), emoji_img)  # 轉換為整數
                cursor_x += emoji_img.width + 2
        else:
            draw.text((int(cursor_x), int(y)), char, font=base_font, fill="black")  # 轉換為整數
            cursor_x += base_font.getlength(char)
    
    # 在函數最後加入游標繪製的邏輯
    """
    █ (實心方塊)
    ▎ (細直線)
    | (直線)
    _ (底線)
    ▁ (底線)
    ⎸ (細直線)
    """
    if show_cursor:
        cursor_char = "█"  # 你可以改用其他字元，例如 "|" 或 "▎"
        draw.text((int(cursor_x), int(y)), cursor_char, font=base_font, fill="black")
    
    return cursor_x - x

# 計算畫布大小
lines = text.split('\n')
temp_img = Image.new("RGB", (1, 1))
draw = ImageDraw.Draw(temp_img)
max_width = 0
total_height = padding

for line in lines:
    # 計算每行的寬度和高度
    line_width = 0
    max_height = 0
    for char in line:
        if is_emoji(char):
            # 為 emoji 預留更多空間
            char_width = 32  # emoji 的預設寬度
            char_height = 32  # emoji 的預設高度
        else:
            char_width = base_font.getlength(char)
            char_height = base_font.getbbox(char)[3]
        line_width += char_width
        max_height = max(max_height, char_height)
    
    max_width = max(max_width, line_width)
    total_height += max_height + line_spacing

# 加入這行來為游標預留空間
max_width += base_font.getlength("X")

total_height += padding
width = int(max_width + padding * 2)
height = int(total_height)

# 建立每一個幀來模擬打字效果
frames = []
total_chars = len(text)

# 每個字符只生成一幀
for i in range(total_chars + 1):
    current_text = text[:i]
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # 從上方邊界開始繪製每一行文字
    y_text = padding
    for line in current_text.split('\n'):
        draw_text_with_emoji(draw, line, padding, y_text, base_font, emoji_font, 
                           show_cursor=(line == current_text.split('\n')[-1]))
        line_height = max(base_font.getbbox("X")[3],
                         32 if any(is_emoji(c) for c in line) else 0)
        y_text += line_height + line_spacing
    frames.append(img)

# 設定每一幀的持續時間
durations = [100] * len(frames)  # 每幀 100ms
durations[-1] = 2000            # 最後一幀停留 2 秒

# 儲存成 GIF 文件
gif_filename = "./asset/helloworld_animation.gif"
frames[0].save(
    gif_filename,
    save_all=True,
    append_images=frames[1:],
    optimize=False,
    duration=durations,  # 使用自定義的持續時間
    loop=0         # 0 表示無限循環
)

print(f"GIF 已經生成並儲存為 {gif_filename}")
