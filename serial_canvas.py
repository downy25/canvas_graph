import struct
import tkinter as tk
import time
import threading
import serial


INTERVAL = 0.01  # 10ms
DATA_LENGTH = 500  # 가로축 데이터 개수
data_values = []  # 수신된 데이터를 저장

def receive_data():
    global data_values

    ser = serial.Serial('COM3', 115200, timeout=1)

    while True:
        data = ser.readline().decode('utf-8').strip()
        if data:
            try:
                data = float(data)
                print(data)
                data_values.append(data)
                if len(data_values) > DATA_LENGTH: 
                    data_values.pop(0)
                time.sleep(INTERVAL)
            except:
                pass

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Graph")
        
        # 창 크기 변경 가능하도록 설정
        self.root.resizable(True, True)
        self.root.bind("<Configure>", self.on_resize)
        
        # 초기 캔버스 크기 설정
        self.canvas_width = 500
        self.canvas_height = 300
        
        # 두 개의 캔버스를 생성
        self.canvas1 = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas2 = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")

        self.canvas1.pack(fill=tk.BOTH, expand=True)
        self.canvas2.pack(fill=tk.BOTH, expand=True)
        self.active_canvas = self.canvas1

        self.update_graph()

    def on_resize(self, event):
        if event.widget == self.root:
            self.canvas_width = event.width
            self.canvas_height = event.height
            self.canvas1.config(width=self.canvas_width, height=self.canvas_height)
            self.canvas2.config(width=self.canvas_width, height=self.canvas_height)

    def update_graph(self):
        if len(data_values) > 1:
            self.draw_graph()
        self.root.after(int(INTERVAL * 1000), self.update_graph)

    def draw_graph(self):
        canvas = self.canvas1 if self.active_canvas == self.canvas2 else self.canvas2
        canvas.delete("all")  # 기존 그래프 지우기
        
        if len(data_values) > 1:
            x_scale = self.canvas_width / max(1, len(data_values))
            y_min = min(data_values)
            y_max = max(data_values)
            y_range = y_max - y_min if y_max != y_min else 1
            y_scale = self.canvas_height / y_range
            
            for i in range(1, len(data_values)):
                x1 = (i - 1) * x_scale
                y1 = self.canvas_height - (data_values[i - 1] - y_min) * y_scale
                x2 = i * x_scale
                y2 = self.canvas_height - (data_values[i] - y_min) * y_scale
                canvas.create_line(x1, y1, x2, y2, fill="blue")
            
            # 세로축 값 표시
            for i in range(5):
                value = y_min + (y_range / 4) * i
                y_pos = self.canvas_height - (value - y_min) * y_scale
                canvas.create_text(20, y_pos, text=f"{value:.2f}", anchor=tk.W, fill="black")
        
        self.active_canvas.pack_forget()
        canvas.pack(fill=tk.BOTH, expand=True)
        self.active_canvas = canvas

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    
    # 데이터 수신 스레드 시작
    thread = threading.Thread(target=receive_data, daemon=True)
    thread.start()
    
    root.mainloop()






















# '''
# 파이썬으로 다음과 같은 프로그램을 제작해줘
# 1. 이더넷 소켓으로 10ms주기로 16진수 명령인 02 c0 03을 보낸다.
# 2. 이더넷 서버의 주소는 192.168.0.7이고 포트는 5000번인다.
# 3. 명령을 보내면 응답 코드는 02 C0 XX XX XX XX 03과 같이 수신된다.
# 4. XX의 4바이트는 리틀앤디안으로 float형식으로 복구한다.
# 5. 만들어진 데이터를 그래프로 표시한다.
# 6. 그래프는 tkinter의 캔버스를 이용한다.
# 7. 캔버스는 2개를 생성한다.
# 8, 첫번째 캔버스의 그림이 그려지는 동안에는 두번째 캔버스가 화면에 보여진다.
# 9. 두번째 캔버스의 그림이 그려지는 동안에는 첫번째 캔버스가 화면에 보여진다.
# 10. 이와같은 방법으로 2개의 캔버스가 서로 교차되면서 표시되면 캔버스에 선이 그려지는 깜빡임을 제거할 수 있다.
# 11. 가로축의 데이터는 150개이다.
# 12. 세로축에는 값을 표시한다.
# 13. 창의 크기를 변경하면 캔버스의 크기도 같이 변화된다.
# '''
# import socket
# import struct
# import tkinter as tk
# import time
# import threading

# # 서버 정보
# HOST = "192.168.0.7"
# PORT = 5000
# COMMAND = bytes([0x02, 0xC0, 0x03])
# INTERVAL = 0.01  # 10ms
# DATA_LENGTH = 500  # 가로축 데이터 개수

# data_values = []  # 수신된 데이터를 저장

# def receive_data():
#     global data_values
    
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         while True:
#             s.sendall(COMMAND)
#             data = s.recv(7)  # 응답 데이터 길이: 7바이트 (02 C0 XX XX XX XX 03)
#             if len(data) == 7 and data[0] == 0x02 and data[1] == 0xC0 and data[-1] == 0x03:
#                 float_value = struct.unpack('<f', data[2:6])[0]  # 리틀 엔디안 float 변환
#                 data_values.append(float_value)
#                 if len(data_values) > DATA_LENGTH:  # 최대 150개 데이터 저장
#                     data_values.pop(0)
#             time.sleep(INTERVAL)

# class GraphApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Real-time Graph")
        
#         # 창 크기 변경 가능하도록 설정
#         self.root.resizable(True, True)
#         self.root.bind("<Configure>", self.on_resize)
        
#         # 초기 캔버스 크기 설정
#         self.canvas_width = 500
#         self.canvas_height = 300
        
#         # 두 개의 캔버스를 생성
#         self.canvas1 = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
#         self.canvas2 = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")

#         self.canvas1.pack(fill=tk.BOTH, expand=True)
#         self.canvas2.pack(fill=tk.BOTH, expand=True)
#         self.active_canvas = self.canvas1

#         self.update_graph()

#     def on_resize(self, event):
#         if event.widget == self.root:
#             self.canvas_width = event.width
#             self.canvas_height = event.height
#             self.canvas1.config(width=self.canvas_width, height=self.canvas_height)
#             self.canvas2.config(width=self.canvas_width, height=self.canvas_height)

#     def update_graph(self):
#         if len(data_values) > 1:
#             self.draw_graph()
#         self.root.after(int(INTERVAL * 1000), self.update_graph)

#     def draw_graph(self):
#         canvas = self.canvas1 if self.active_canvas == self.canvas2 else self.canvas2
#         canvas.delete("all")  # 기존 그래프 지우기
        
#         if len(data_values) > 1:
#             x_scale = self.canvas_width / max(1, len(data_values))
#             y_min = min(data_values)
#             y_max = max(data_values)
#             y_range = y_max - y_min if y_max != y_min else 1
#             y_scale = self.canvas_height / y_range
            
#             for i in range(1, len(data_values)):
#                 x1 = (i - 1) * x_scale
#                 y1 = self.canvas_height - (data_values[i - 1] - y_min) * y_scale
#                 x2 = i * x_scale
#                 y2 = self.canvas_height - (data_values[i] - y_min) * y_scale
#                 canvas.create_line(x1, y1, x2, y2, fill="blue")
            
#             # 세로축 값 표시
#             for i in range(5):
#                 value = y_min + (y_range / 4) * i
#                 y_pos = self.canvas_height - (value - y_min) * y_scale
#                 canvas.create_text(20, y_pos, text=f"{value:.2f}", anchor=tk.W, fill="black")
        
#         self.active_canvas.pack_forget()
#         canvas.pack(fill=tk.BOTH, expand=True)
#         self.active_canvas = canvas

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = GraphApp(root)
    
#     # 데이터 수신 스레드 시작
#     thread = threading.Thread(target=receive_data, daemon=True)
#     thread.start()
    
#     root.mainloop()






    
