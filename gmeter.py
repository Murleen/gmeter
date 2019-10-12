import socket
import struct
import sys
import select
import math

IP = '127.0.0.1'
PORT = 4321

G = 9.81

st = struct.Struct("2I9f")

sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

with open('gmeter.csv', 'w') as f:
    f.write('Time,Surge,Sway,Heave\n')

    while True:
        rlist, _, _ = select.select([sock], [], [], 1)
        if sock in rlist:
            data=sock.recv(st.size)
            pid, tick, yaw, pitch, roll, spin_x, spin_y, spin_z, acc_x, acc_y, acc_z = st.unpack(data)
            surge = acc_x / G
            sway = acc_y / G
            heave = acc_z / G

            gravity = (0, 0, 1)
            gravity = (gravity[0] * math.cos(yaw) + gravity[1] * math.sin(yaw), -gravity[0] * math.sin(yaw) + gravity[1] * math.cos(yaw), gravity[2])
            gravity = (gravity[0] * math.cos(pitch) - gravity[2] * math.sin(pitch), gravity[1], gravity[0] * math.sin(pitch) + gravity[2] * math.cos(pitch))
            gravity = (gravity[0], gravity[1] * math.cos(roll) + gravity[2] * math.sin(roll), -gravity[1] * math.sin(roll) + gravity[2] * math.cos(roll))

            surge += gravity[0]
            sway += gravity[1]
            heave += gravity[2]

            print('Surge: {: 2.2f}g Sway: {: 2.2f}g Heave: {: 2.2f}g          '.format(surge, sway, heave), end='\r')
            sys.stdout.flush()
            f.write('{:f},{:f},{:f},{:f}\n'.format(tick/50, surge, sway, heave))
