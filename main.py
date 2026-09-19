from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # ファイルを受け取る
        if 'image' not in request.files:
            return {'error': 'ファイルがアップロードされていません'}, 400
        
        file = request.files['image']
        if file.filename == '':
            return {'error': 'ファイルが選択されていません'}, 400
        
        # 分割数と分割方向を受け取る
        split_count = int(request.form.get('split_count', 4))
        direction = request.form.get('direction', 'vertical')
        
        if split_count < 2 or split_count > 10:
            return {'error': '分割数は2～10の間で指定してください'}, 400
        
        # 画像を読み込む
        img = Image.open(file.stream).convert('RGB')
        width, height = img.size
        
        # GIFフレームを生成
        frames = []
        durations = []
        
        if direction == 'vertical':
            # 縦分割（左から右へ）
            frame_width = width // split_count
            for i in range(1, split_count + 1):
                frame = Image.new('RGB', (width, height), 'white')
                display_width = frame_width * i
                crop_box = (0, 0, display_width, height)
                cropped = img.crop(crop_box)
                frame.paste(cropped, (0, 0))
                frames.append(frame)
                durations.append(1000)
        else:
            # 横分割（上から下へ）
            frame_height = height // split_count
            for i in range(1, split_count + 1):
                frame = Image.new('RGB', (width, height), 'white')
                display_height = frame_height * i
                crop_box = (0, 0, width, display_height)
                cropped = img.crop(crop_box)
                frame.paste(cropped, (0, 0))
                frames.append(frame)
                durations.append(1000)
        
        # GIFを生成
        output = io.BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0
        )
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/gif',
            as_attachment=True,
            download_name='divider-animation.gif'
        )
    
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # localhostで実行
    print('✓ ブラウザで http://localhost:5000 を開いてください')
    app.run(host='localhost', port=5000, debug=False)