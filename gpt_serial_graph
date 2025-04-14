import struct
import tkinter as tk
import time
import threading
import serial

INTERVAL = 0.01  # 10ms
DATA_LENGTH = 500
data_values = []

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
            except Exception as e:
                print(f"Error parsing data: {e}")

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Graph with Buttons")

        # 전체 프레임 구성 (상단 버튼 + 하단 그래프)
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.graph_frame = tk.Frame(root)
        self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 버튼 4개 추가
        self.button1 = tk.Button(self.top_frame, text="버튼 1", command=lambda: print("버튼 1 클릭"))
        self.button2 = tk.Button(self.top_frame, text="버튼 2", command=lambda: print("버튼 2 클릭"))
        self.button3 = tk.Button(self.top_frame, text="버튼 3", command=lambda: print("버튼 3 클릭"))
        self.button4 = tk.Button(self.top_frame, text="버튼 4", command=lambda: print("버튼 4 클릭"))

        self.button1.pack(side=tk.LEFT, padx=5)
        self.button2.pack(side=tk.LEFT, padx=5)
        self.button3.pack(side=tk.LEFT, padx=5)
        self.button4.pack(side=tk.LEFT, padx=5)

        # 그래프용 캔버스 2개 (double buffering)
        self.canvas_width = 500
        self.canvas_height = 300
        self.canvas1 = tk.Canvas(self.graph_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas2 = tk.Canvas(self.graph_frame, width=self.canvas_width, height=self.canvas_height, bg="white")

        self.canvas1.pack(fill=tk.BOTH, expand=True)
        self.canvas2.pack_forget()
        self.active_canvas = self.canvas1

        self.root.bind("<Configure>", self.on_resize)

        self.update_graph()

    def on_resize(self, event):
        if event.widget == self.root:
            self.canvas_width = self.graph_frame.winfo_width()
            self.canvas_height = self.graph_frame.winfo_height()
            self.canvas1.config(width=self.canvas_width, height=self.canvas_height)
            self.canvas2.config(width=self.canvas_width, height=self.canvas_height)

    def update_graph(self):
        if len(data_values) > 1:
            self.draw_graph()
        self.root.after(int(INTERVAL * 1000), self.update_graph)

    def draw_graph(self):
        canvas = self.canvas1 if self.active_canvas == self.canvas2 else self.canvas2
        canvas.delete("all")

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

    thread = threading.Thread(target=receive_data, daemon=True)
    thread.start()

    root.mainloop()
