import subprocess
import time
import pdb

p = subprocess.Popen('pianobar', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
time.sleep(3)

i = 0
print '=========== start loops ============'
while i < 2:
   time.sleep(3)
   p.stdin.write('i')
   #p.stdin.write(str(i) + '\r\n')
   #p.stdout.read()
   p.stdout.flush()
   j = 0
   #while j < 10:
   #  print p.stdout.read(100)
   #  j += 1
   while True:
      line = p.stdout.readline()
      if line != '':
          print '====== %s =======' % line
      else:
          break
   pdb.set_trace()  
   
   for line in iter(p.stdout.readline, b''):
      print(">>> " + line.rstrip())

  
   i = i + 1
   print '=========== end loop ============'
p.stdin.write('q')   
