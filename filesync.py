import asyncio
import functools
import os
import shutil
from concurrent.futures import CancelledError

loop = asyncio.get_event_loop()

class FileSync:
  def __init__(self, from_dir, to_dir):
    self.from_dir = from_dir
    self.to_dir = to_dir

  async def move_files(self):
    if not os.path.isdir(self.from_dir):
      return False
    if not os.path.isdir(self.to_dir):
      return False

    transfers = []
    for src_root, dirs, files in os.walk(self.from_dir):
      post_fix = src_root[len(self.from_dir):]
      while len(post_fix) > 0 and post_fix[0] == os.sep:
        post_fix = post_fix[1:]
      dst_root = os.path.join(self.to_dir, post_fix)
      for f in files:
        src = os.path.join(src_root, f)
        dst = os.path.join(dst_root, f)
        transfers.append({'src':src, 'dst':dst, 'retries':0})

    for idx, t in enumerate(transfers):
      if not os.path.isdir(self.to_dir):
        continue
      if not os.path.isdir(self.from_dir):
        continue

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

      msg = '[{}%]'.format((idx+1)*100.0 / len(t))
      if src_size > dst_size or (src_size == dst_size and src_mtime > dst_mtime):
        print(msg, '{}{} -> {}'.format('replace ' if dst_size != 0 else '', src, dst))
        await loop.run_in_executor(None, functools.partial(os.makedirs, os.path.dirname(dst), exist_ok=True))
        try:
          await loop.run_in_executor(None, shutil.move, src, dst)
        except CancelledError as ce:
          pass
        except Exception as e:
          print(e)
      else:
        try:
          print(msg, 'Removing: {}'.format(src))
          await loop.run_in_executor(None, os.remove(src))
        except OSError as e:
          print(e)

    return True

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Sync files')
  parser.add_argument('src', metavar='SRC', type=str, nargs=1, help='Source directory')
  parser.add_argument('dst', metavar='DST', type=str, nargs=1, help='Destination directory')
  args = parser.parse_args()
  
  filesync = FileSync(args.src[0], args.dst[0])
  loop.run_until_complete(filesync.move_files())
  loop.close()
