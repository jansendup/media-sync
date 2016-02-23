import os
import shutil

class FileSync:
  def __init__(self, from_dir, to_dir):
    self.from_dir = from_dir
    self.to_dir = to_dir

  def move_files():
    if not os.path.isdir(self.from_dir):
      return False
    if not os.path.isdir(self.to_dir):
      return False

    transfers = []
    for src_root, dirs, files in os.walk(self.from_dir):
      dst_root = src_root[len(self.from_dir):]
      for f in files:
        src = os.path.join(root, f)
        dst = os.path.join(dst_root, f)
        transfers.append({'src':src, 'dst':dst, 'retries':0})

    for idx, t in enumerate(transfers):
      src = t['src']
      dst = t['dst']
      st = os.stat(src)
      src_size = st.st_size
      src_mtime = st.st_mtime

      dst_size = 0
      dst_mtime = 0
      if os.path.isfile(dst):
        st = os.stat(dst)
        dst_size = st.st_size
        dst_mtime = st.st_mtime

      msg = '[{}\%]'.format(idx*100.0 / len(t))
      if src_size > dst_size or (src_size == dst_size and src_mtime > dst_mtime):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
          print(msg, '{} -> {}'.format(src, dst))
          shutil.move(src, dst)
        except Exception as e:
          print(e)
      else:
        try:
          print(msg, 'Removing: {}'.format(src))
          os.remove(src)
        except OSError as e:
          print(e)
        
