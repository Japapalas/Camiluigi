import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading
import os
import subprocess

# Function to find ffmpeg and ffprobe in the directory tree
def find_ffmpeg_and_ffprobe(start_dir):
    ffmpeg_path = None
    ffprobe_path = None
    for root, dirs, files in os.walk(start_dir):
        if 'ffmpeg.exe' in files:
            ffmpeg_path = os.path.join(root, 'ffmpeg.exe')
        if 'ffprobe.exe' in files:
            ffprobe_path = os.path.join(root, 'ffprobe.exe')
        if ffmpeg_path and ffprobe_path:
            break
    return ffmpeg_path, ffprobe_path

# Get the directory where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH, FFPROBE_PATH = find_ffmpeg_and_ffprobe(script_dir)

def fetch_video_info(url, progress_callback):
    ydl_opts = {
        'listformats': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
    return result

def download_youtube_video(url, download_path, format_id, progress_callback):
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'format': format_id,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        },
        'progress_hooks': [progress_callback],
        'ffmpeg_location': FFMPEG_PATH,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Sucesso", f"Vídeo baixado com sucesso e salvo em: {download_path}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao baixar o vídeo: {e}")

def download_instagram_video(url, download_path, progress_callback):
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        },
        'progress_hooks': [progress_callback],
        'ffmpeg_location': FFMPEG_PATH,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Sucesso", f"Vídeo baixado com sucesso e salvo em: {download_path}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao baixar o vídeo do Instagram: {e}")

def download_tiktok_video(url, download_path, progress_callback):
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        },
        'progress_hooks': [progress_callback],
        'ffmpeg_location': FFMPEG_PATH,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4',
        }],
        'writethumbnail': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            formats = result.get('formats', None)
            if formats:
                for f in formats:
                    format_note = f.get('format_note')
                    if format_note and 'no_watermark' in format_note.lower():
                        ydl_opts['format'] = f['format_id']
                        break
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        messagebox.showinfo("Sucesso", f"Vídeo baixado com sucesso e salvo em: {download_path}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao baixar o vídeo do TikTok: {e}")

def download_youtube_audio(url, download_path, progress_callback):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        },
        'progress_hooks': [progress_callback],
        'ffmpeg_location': FFMPEG_PATH,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Sucesso", f"Áudio baixado com sucesso e salvo em: {download_path}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao baixar o áudio: {e}")

def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, directory)

def fetch_formats():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo.")
        return
    progress_bar['value'] = 0
    progress_label.config(text="Buscando formatos...")
    thread = threading.Thread(target=fetch_formats_thread, args=(url,))
    thread.start()

def fetch_formats_thread(url):
    video_info = fetch_video_info(url, update_progress_fetch)
    format_list = video_info['formats']
    valid_resolutions = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p']
    format_combobox['values'] = ()
    for fmt in format_list:
        format_id = fmt['format_id']
        ext = fmt['ext']
        resolution = fmt.get('format_note', 'N/A')
        if ext == 'mp4' and resolution in valid_resolutions:
            format_combobox['values'] = (*format_combobox['values'], f"{format_id} - {ext} - {resolution}")
    progress_bar['value'] = 100
    progress_label.config(text="Formatos encontrados")

def start_download():
    url = url_entry.get()
    download_path = directory_entry.get()
    selected_format = format_combobox.get()
    if not url or not download_path or not selected_format:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo, selecione o diretório de download e escolha a qualidade do vídeo.")
        return
    format_id = selected_format.split(" - ")[0]
    progress_bar['value'] = 0
    progress_label.config(text="Baixando vídeo...")
    thread = threading.Thread(target=download_thread, args=(url, download_path, format_id))
    thread.start()

def download_thread(url, download_path, format_id):
    download_youtube_video(url, download_path, format_id, update_progress_download)

def start_instagram_download():
    url = url_instagram_entry.get()
    download_path = directory_instagram_entry.get()
    if not url or not download_path:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo do Instagram e selecione o diretório de download.")
        return
    progress_bar_instagram['value'] = 0
    progress_label_instagram.config(text="Baixando vídeo...")
    thread = threading.Thread(target=download_instagram_thread, args=(url, download_path))
    thread.start()

def download_instagram_thread(url, download_path):
    download_instagram_video(url, download_path, update_progress_instagram_download)

def start_tiktok_download():
    url = url_tiktok_entry.get()
    download_path = directory_tiktok_entry.get()
    if not url or not download_path:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo do TikTok e selecione o diretório de download.")
        return
    progress_bar_tiktok['value'] = 0
    progress_label_tiktok.config(text="Baixando vídeo...")
    thread = threading.Thread(target=download_tiktok_thread, args=(url, download_path))
    thread.start()

def download_tiktok_thread(url, download_path):
    download_tiktok_video(url, download_path, update_progress_tiktok_download)

def start_youtube_mp3_download():
    url = url_youtube_mp3_entry.get()
    download_path = directory_youtube_mp3_entry.get()
    if not url or not download_path:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo do YouTube e selecione o diretório de download.")
        return
    progress_bar_youtube_mp3['value'] = 0
    progress_label_youtube_mp3.config(text="Baixando áudio...")
    thread = threading.Thread(target=download_youtube_mp3_thread, args=(url, download_path))
    thread.start()

def download_youtube_mp3_thread(url, download_path):
    download_youtube_audio(url, download_path, update_progress_youtube_mp3_download)

def update_progress_fetch(d):
    progress_bar['value'] += 10

def update_progress_download(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            percent = downloaded / total * 100
            progress_bar['value'] = percent
            progress_label.config(text=f"Baixando vídeo... {int(percent)}%")
        else:
            progress_label.config(text="Baixando vídeo...")

def update_progress_instagram_download(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            percent = downloaded / total * 100
            progress_bar_instagram['value'] = percent
            progress_label_instagram.config(text=f"Baixando vídeo... {int(percent)}%")
        else:
            progress_label_instagram.config(text="Baixando vídeo...")

def update_progress_tiktok_download(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            percent = downloaded / total * 100
            progress_bar_tiktok['value'] = percent
            progress_label_tiktok.config(text=f"Baixando vídeo... {int(percent)}%")
        else:
            progress_label_tiktok.config(text="Baixando vídeo...")

def update_progress_youtube_mp3_download(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            percent = downloaded / total * 100
            progress_bar_youtube_mp3['value'] = percent
            progress_label_youtube_mp3.config(text=f"Baixando áudio... {int(percent)}%")
        else:
            progress_label_youtube_mp3.config(text="Baixando áudio...")

def compress_video(file_path, quality):
    if not os.path.exists(FFMPEG_PATH):
        messagebox.showerror("Erro", f"FFmpeg não encontrado em: {FFMPEG_PATH}")
        return

    output_path = os.path.splitext(file_path)[0] + f"_compressed_{quality}.mp4"
    if quality == 'whatsapp':
        command = [
            FFMPEG_PATH, '-i', file_path, '-vf', 'scale=640:480', '-c:v', 'libx264', '-preset', 'slow', '-crf', '28', '-c:a', 'aac', '-b:a', '64k', '-y', output_path
        ]
    else:
        crf = '28' if quality == 'medium' else '23'
        command = [
            FFMPEG_PATH, '-i', file_path, '-vf', 'scale=640:480', '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-c:a', 'aac', '-b:a', '64k', '-y', output_path
        ]
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in process.stderr:
            update_progress_compress(line)
        process.wait()
        if process.returncode == 0:
            messagebox.showinfo("Sucesso", f"Vídeo compactado com sucesso para: {output_path}")
        else:
            messagebox.showerror("Erro", f"Erro ao compactar o vídeo: {process.stderr.read().decode('utf-8')}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao compactar o vídeo: {e}")

def start_compression(quality):
    file_path = filedialog.askopenfilename(title="Selecione o Vídeo", filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        progress_bar_compress['value'] = 0
        progress_label_compress.config(text="Compactando vídeo...")
        thread = threading.Thread(target=compress_video, args=(file_path, quality))
        thread.start()

def update_progress_compress(line):
    progress_bar_compress['value'] += 1

# Configuração da janela principal
root = tk.Tk()
root.title("CamiLuigi by:Japapala")

notebook = ttk.Notebook(root)
download_frame = ttk.Frame(notebook)
compress_frame = ttk.Frame(notebook)
instagram_frame = ttk.Frame(notebook)
tiktok_frame = ttk.Frame(notebook)
youtube_mp3_frame = ttk.Frame(notebook)
notebook.add(download_frame, text="Baixar Vídeo")
notebook.add(compress_frame, text="Compactar Vídeo")
notebook.add(instagram_frame, text="Baixar Instagram")
notebook.add(tiktok_frame, text="Baixar TikTok")
notebook.add(youtube_mp3_frame, text="YT para MP3")
notebook.grid(row=0, column=0, padx=10, pady=10)

# GUI para baixar vídeos do YouTube
tk.Label(download_frame, text="Link do Vídeo do YouTube:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(download_frame, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)
fetch_button = tk.Button(download_frame, text="Buscar Formatos", command=fetch_formats)
fetch_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(download_frame, text="Diretório para Salvar o Vídeo:").grid(row=1, column=0, padx=10, pady=10)
directory_entry = tk.Entry(download_frame, width=50)
directory_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(download_frame, text="Procurar", command=lambda: browse_directory(directory_entry))
browse_button.grid(row=1, column=2, padx=10, pady=10)

tk.Label(download_frame, text="Escolha a Qualidade do Vídeo:").grid(row=2, column=0, padx=10, pady=10)
format_combobox = ttk.Combobox(download_frame, width=47)
format_combobox.grid(row=2, column=1, padx=10, pady=10)

progress_bar = ttk.Progressbar(download_frame, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=3, column=1, padx=10, pady=10)
progress_label = tk.Label(download_frame, text="")
progress_label.grid(row=4, column=1, padx=10, pady=10)

download_button = tk.Button(download_frame, text="Baixar Vídeo", command=start_download)
download_button.grid(row=5, column=1, padx=10, pady=20)

# GUI para compactar vídeos
tk.Label(compress_frame, text="Selecione o Vídeo para Compactar:").grid(row=0, column=0, padx=10, pady=10)
compress_whatsapp_button = tk.Button(compress_frame, text="Compactar para WhatsApp", command=lambda: start_compression('whatsapp'))
compress_whatsapp_button.grid(row=1, column=0, padx=10, pady=10)
compress_medium_button = tk.Button(compress_frame, text="Medium", command=lambda: start_compression('medium'))
compress_medium_button.grid(row=1, column=1, padx=10, pady=10)
compress_high_button = tk.Button(compress_frame, text="High", command=lambda: start_compression('high'))
compress_high_button.grid(row=1, column=2, padx=10, pady=10)

progress_bar_compress = ttk.Progressbar(compress_frame, orient='horizontal', length=400, mode='determinate')
progress_bar_compress.grid(row=2, column=1, padx=10, pady=10)
progress_label_compress = tk.Label(compress_frame, text="")
progress_label_compress.grid(row=3, column=1, padx=10, pady=10)

# GUI para baixar vídeos do Instagram
tk.Label(instagram_frame, text="Link do Vídeo do Instagram:").grid(row=0, column=0, padx=10, pady=10)
url_instagram_entry = tk.Entry(instagram_frame, width=50)
url_instagram_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(instagram_frame, text="Diretório para Salvar o Vídeo:").grid(row=1, column=0, padx=10, pady=10)
directory_instagram_entry = tk.Entry(instagram_frame, width=50)
directory_instagram_entry.grid(row=1, column=1, padx=10, pady=10)
browse_instagram_button = tk.Button(instagram_frame, text="Procurar", command=lambda: browse_directory(directory_instagram_entry))
browse_instagram_button.grid(row=1, column=2, padx=10, pady=10)

progress_bar_instagram = ttk.Progressbar(instagram_frame, orient='horizontal', length=400, mode='determinate')
progress_bar_instagram.grid(row=2, column=1, padx=10, pady=10)
progress_label_instagram = tk.Label(instagram_frame, text="")
progress_label_instagram.grid(row=3, column=1, padx=10, pady=10)

download_instagram_button = tk.Button(instagram_frame, text="Baixar Vídeo", command=start_instagram_download)
download_instagram_button.grid(row=4, column=1, padx=10, pady=20)

# GUI para baixar vídeos do TikTok
tk.Label(tiktok_frame, text="Link do Vídeo do TikTok:").grid(row=0, column=0, padx=10, pady=10)
url_tiktok_entry = tk.Entry(tiktok_frame, width=50)
url_tiktok_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(tiktok_frame, text="Diretório para Salvar o Vídeo:").grid(row=1, column=0, padx=10, pady=10)
directory_tiktok_entry = tk.Entry(tiktok_frame, width=50)
directory_tiktok_entry.grid(row=1, column=1, padx=10, pady=10)
browse_tiktok_button = tk.Button(tiktok_frame, text="Procurar", command=lambda: browse_directory(directory_tiktok_entry))
browse_tiktok_button.grid(row=1, column=2, padx=10, pady=10)

progress_bar_tiktok = ttk.Progressbar(tiktok_frame, orient='horizontal', length=400, mode='determinate')
progress_bar_tiktok.grid(row=2, column=1, padx=10, pady=10)
progress_label_tiktok = tk.Label(tiktok_frame, text="")
progress_label_tiktok.grid(row=3, column=1, padx=10, pady=10)

download_tiktok_button = tk.Button(tiktok_frame, text="Baixar Vídeo", command=start_tiktok_download)
download_tiktok_button.grid(row=4, column=1, padx=10, pady=20)

# GUI para converter vídeos do YouTube para MP3
tk.Label(youtube_mp3_frame, text="Link do Vídeo do YouTube:").grid(row=0, column=0, padx=10, pady=10)
url_youtube_mp3_entry = tk.Entry(youtube_mp3_frame, width=50)
url_youtube_mp3_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(youtube_mp3_frame, text="Diretório para Salvar o Áudio:").grid(row=1, column=0, padx=10, pady=10)
directory_youtube_mp3_entry = tk.Entry(youtube_mp3_frame, width=50)
directory_youtube_mp3_entry.grid(row=1, column=1, padx=10, pady=10)
browse_youtube_mp3_button = tk.Button(youtube_mp3_frame, text="Procurar", command=lambda: browse_directory(directory_youtube_mp3_entry))
browse_youtube_mp3_button.grid(row=1, column=2, padx=10, pady=10)

progress_bar_youtube_mp3 = ttk.Progressbar(youtube_mp3_frame, orient='horizontal', length=400, mode='determinate')
progress_bar_youtube_mp3.grid(row=2, column=1, padx=10, pady=10)
progress_label_youtube_mp3 = tk.Label(youtube_mp3_frame, text="")
progress_label_youtube_mp3.grid(row=3, column=1, padx=10, pady=10)

download_youtube_mp3_button = tk.Button(youtube_mp3_frame, text="Baixar Áudio", command=start_youtube_mp3_download)
download_youtube_mp3_button.grid(row=4, column=1, padx=10, pady=20)

# Check if ffmpeg and ffprobe are found after window creation
if not FFMPEG_PATH or not FFPROBE_PATH:
    messagebox.showerror("Erro", "Não foi possível encontrar ffmpeg.exe e ffprobe.exe. Certifique-se de que eles estejam no diretório ou em um subdiretório.")

root.mainloop()
