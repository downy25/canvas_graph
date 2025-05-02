import struct
import tkinter as tk
import time
import threading
import serial

INTERVAL = 0.0001
data_values = []
prv_value = 0.0

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Graph with Buttons")

        # speed
        self.interver = 0.001

        # 시리얼 포트 열기
        self.ser = serial.Serial('COM4', 576000, timeout=1)

        self.DATA_LENGTH = 1000 # 데이터 갯수
        self.data_count = 0
        self.time_button = 0
        
        #그래프 스케일
        self.ymin_s = -10
        self.ymax_s =  10
        self.show_line = 20
        self.weight = 1.0
        self.count = 0
        
        self.ready_to_draw = False
        self.last_time = time.time()

        # 프레임 구성
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.graph_frame = tk.Frame(root)
        self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 버튼들 (시그널 전송)
        self.button1 = tk.Button(self.top_frame, text="VOLTS/DIV", command=lambda: self.send_signal('1'))
        self.pause_button = tk.Button(self.top_frame, text="⏸️ 정지", command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.button1.pack(side=tk.LEFT, padx=10)
        self.fast_button = tk.Button(self.top_frame, text="TIME/DIV", command=self.time_div)
        self.fast_button.pack(side=tk.LEFT, padx=12)

        self.is_paused = False  # 그래프 흐름 정지 여부

        # 캔버스 크기 설정 (x:1000, y:500)
        self.canvas_width = 1000
        self.canvas_height = 500
        self.canvas1 = tk.Canvas(self.graph_frame, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas2 = tk.Canvas(self.graph_frame, width=self.canvas_width, height=self.canvas_height, bg="white")

        self.canvas1.pack(padx=10, pady=10)  # 자동 확장 X
        self.canvas2.pack_forget()
        self.active_canvas = self.canvas1

        # 데이터 수신 스레드 시작
        self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
        self.receive_thread.start()

        self.update_graph()

    def time_div(self):
        self.time_button = self.time_button + 1
        if(self.time_button == 2): self.time_button = 0
        self.data_count = 0


        

    def send_signal(self, signal_char):
        try:
            self.ser.write(signal_char.encode('utf-8'))
            print(f"Sent signal: {signal_char}")
            self.count = self.count + 1
            if(self.count == 3): self.count = 0

            if(self.count == 1):
                self.ymin_s = -10
                self.ymax_s =  10
                self.show_line = 20
                self.weight = 2.0
            elif(self.count == 2):
                self.ymin_s = -5
                self.ymax_s =  5
                self.show_line = 10
                self.weight = 1.0
            else : 
                self.ymin_s = -10
                self.ymax_s =  10
                self.show_line = 20
                self.weight = 1.0



        except Exception as e:
            print(f"Error sending signal: {e}")

    def receive_data(self):
        global data_values
        global prv_value
        while True:
            if len(data_values) >= self.DATA_LENGTH:
                self.ready_to_draw = True
                time.sleep(0.0001)  # 너무 빠른 루프 방지
                continue
            try:
                # data = self.ser.read(7)  # 응답 데이터 길이: 7바이트 (02 C0 XX XX XX XX 03)
                # print(data)
                # if len(data) == 7 and data[0] == 0x02 and data[1] == 0xC0 and data[-1] == 0x03:
                #     float_value = struct.unpack('<f', data[2:6])[0]  # 리틀 엔디안 float 변환
                #     data_values.append(float_value)
                #     if len(data_values) > DATA_LENGTH:  # 최대 150개 데이터 저장
                #         data_values.pop(0)
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    try:
                        value = int(data)+700   ##바이어스 만큼 올림 --> 실험적으로 찾음음
                        #print(value)
                        # -5.0 ~ 5.0로 정규화
                        f_value = float((value - 2048) / 2047) * 5.0
                        if(self.time_button == 1):
                            self.data_count = self.data_count + 1
                            if(self.data_count % 20 == 0):
                                data_values.append(f_value)
                            else:
                                pass

                            if(self.data_count == 19): self.data_count = 0
                        else :
                            data_values.append(f_value)
                                

                        # 값이 원하는 값이 들어오지 않으면 처리리         
                        if f_value > 3.3 or f_value < 0.1:
                            data_values.append(prv_value)
                        else:
                            data_values.append(f_value)


                        prv_value = f_value

                    except ValueError:
                        data_values.append(prv_value)
            except Exception as e:
                print(f"Error receiving data: {e}")

            
                
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.config(text="▶️ 재생" if self.is_paused else "⏸️ 정지")

    def on_resize(self, event):
        # 크기 조정 방지
        pass

    def update_graph(self):
        if not self.is_paused and self.ready_to_draw:
            current_time = time.time()  # 조건에 들어가기 직전 시간 기록
            # 이전 시간과 비교하여 경과 시간 계산
            elapsed_time = current_time - self.last_time
            print(f"Time elapsed since last update: {elapsed_time:.6f} seconds")
            # 현재 시간을 마지막 시간으로 업데이트
            self.last_time = current_time
            self.draw_graph()
            data_values.clear()
            self.ready_to_draw = False
        self.root.after(int(INTERVAL * 10000), self.update_graph)


    def draw_graph(self):
        canvas = self.canvas1  # 항상 보여지는 canvas1에 그리기
        canvas.delete("all")

        x_range = self.DATA_LENGTH
        step = int(self.DATA_LENGTH/10)

        y_min = self.ymin_s 
        y_max = self.ymax_s 
        y_range = y_max - y_min  # = 10.0
        y_scale = self.canvas_height / y_range  # = 500 / 10 = 50.0 픽셀/Volt

        x_scale = self.canvas_width / (x_range - 1)
        y_scale = self.canvas_height / y_range

        # 점선 그리드 (Y축 0.3 단위)
        for i in range(self.show_line):
            y_val = y_min + i * self.weight
            y = self.canvas_height - (y_val - y_min) * y_scale
            canvas.create_line(0, y, self.canvas_width, y, fill="#ccc", dash=(2, 4))
            canvas.create_text(5, y, anchor='nw', text=f"{y_val:.1f}V", fill="white")

        # 점선 그리드 (X축 10 단위)
        for i in range(0, x_range + 1, step):
            x = i * x_scale
            canvas.create_line(x, 0, x, self.canvas_height, fill="#ccc", dash=(2, 4))

        # 그래프 그리기
        if len(data_values) > 1:
            try:
                for i in range(1, len(data_values)):
                    y1_val = float(data_values[i - 1])*3.0
                    y2_val = float(data_values[i])*3.0

                    x1 = (i - 1) * x_scale
                    y1 = self.canvas_height - (y1_val - y_min) * y_scale
                    x2 = i * x_scale
                    y2 = self.canvas_height - (y2_val - y_min) * y_scale

                    canvas.create_line(x1, y1, x2, y2, fill="#FFFF00")
            except ValueError as e:
                print(f"Invalid data in data_values: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
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






    
