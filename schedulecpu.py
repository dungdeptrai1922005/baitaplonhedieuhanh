import tkinter as tk
from tkinter import messagebox, ttk

class CPUSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng CPU Scheduler")
        self.processes = []
        # Title
        tk.Label(root, text="CPU Scheduling Simulation", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=5, pady=10)
        # Input labels
        tk.Label(root, text="PID").grid(row=1, column=0)
        tk.Label(root, text="Arrival").grid(row=1, column=1)
        tk.Label(root, text="Burst").grid(row=1, column=2)
        # Input fields
        self.pid = tk.Entry(root, width=8)
        self.arrival = tk.Entry(root, width=8)
        self.burst = tk.Entry(root, width=8)
        self.pid.grid(row=2, column=0)
        self.arrival.grid(row=2, column=1)
        self.burst.grid(row=2, column=2)
        tk.Button(root, text="Thêm", command=self.add_process).grid(row=2, column=3)
        # Treeview for process list
        columns = ("PID", "Arrival", "Burst")
        self.process_tree = ttk.Treeview(root, columns=columns, show="headings", height=5)
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, anchor='center', width=80)
        self.process_tree.grid(row=3, column=0, columnspan=5, pady=5)
        # Algorithm selection
        self.algo = tk.StringVar(value="FCFS")
        tk.Label(root, text="Thuật toán:").grid(row=4, column=0, sticky='e')
        algo_menu = tk.OptionMenu(root, self.algo, "FCFS", "SJF", "RR", command=self.toggle_quanta)
        algo_menu.grid(row=4, column=1, sticky='w')
        # Quanta input for RR
        self.quanta_label = tk.Label(root, text="Quanta:")
        self.quanta_entry = tk.Entry(root, width=5)
        # Run button
        tk.Button(root, text="Chạy", command=self.run_simulation).grid(row=4, column=3, columnspan=2)
        # Output
        self.output = tk.Text(root, height=15, width=60)
        self.output.grid(row=5, column=0, columnspan=5, pady=10)
    def toggle_quanta(self, value):
        if value == "RR":
            self.quanta_label.grid(row=4, column=2)
            self.quanta_entry.grid(row=4, column=3)
        else:
            self.quanta_label.grid_forget()
            self.quanta_entry.grid_forget()

    def add_process(self):
        try:
            p = {
                "pid": self.pid.get(),
                "arrival": int(self.arrival.get()),
                "burst": int(self.burst.get())
            }
            self.processes.append(p)
            self.process_tree.insert("", tk.END, values=(p["pid"], p["arrival"], p["burst"]))
            self.pid.delete(0, tk.END)
            self.arrival.delete(0, tk.END)
            self.burst.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ")

    def run_simulation(self):
        algo = self.algo.get()
        result = ""

        if not self.processes:
            messagebox.showwarning("Chưa có tiến trình", "Vui lòng thêm ít nhất một tiến trình.")
            return

        if algo == "FCFS":
            result = self.fcfs()
        elif algo == "SJF":
            result = self.sjf()
        elif algo == "RR":
            try:
                quanta = int(self.quanta_entry.get())
                if quanta <= 0:
                    raise ValueError
                result = self.rr(quanta)
            except ValueError:
                messagebox.showerror("Lỗi", "Quanta phải là số nguyên dương.")
                return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, result)

    def fcfs(self):
        plist = sorted(self.processes, key=lambda x: x["arrival"])
        time, total_wait, total_turnaround, res = 0, 0, 0, []

        for p in plist:
            start = max(time, p["arrival"])
            wait = start - p["arrival"]
            finish = start + p["burst"]
            turnaround = finish - p["arrival"]
            time = finish
            total_wait += wait
            total_turnaround += turnaround
            res.append(f"{p['pid']}: Start={start}, Finish={finish}, Wait={wait}, Turnaround={turnaround}")

        avg_wait = total_wait / len(plist)
        avg_turn = total_turnaround / len(plist)
        res.append(f"\nAvg Waiting Time: {avg_wait:.2f}")
        res.append(f"Avg Turnaround Time: {avg_turn:.2f}")
        return "\n".join(res)

    def sjf(self):
        plist = sorted(self.processes, key=lambda x: (x["arrival"], x["burst"]))
        ready, time, res = [], 0, []
        total_wait = 0
        total_turnaround = 0

        while plist or ready:
            while plist and plist[0]["arrival"] <= time:
                ready.append(plist.pop(0))
            if ready:
                ready.sort(key=lambda x: x["burst"])
                p = ready.pop(0)
                start = max(time, p["arrival"])
                wait = start - p["arrival"]
                finish = start + p["burst"]
                turnaround = finish - p["arrival"]
                time = finish
                total_wait += wait
                total_turnaround += turnaround
                res.append(f"{p['pid']}: Start={start}, Finish={finish}, Wait={wait}, Turnaround={turnaround}")
            else:
                time += 1

        avg_wait = total_wait / len(self.processes)
        avg_turn = total_turnaround / len(self.processes)
        res.append(f"\nAvg Waiting Time: {avg_wait:.2f}")
        res.append(f"Avg Turnaround Time: {avg_turn:.2f}")
        return "\n".join(res)

    def rr(self, quanta):
        plist = sorted(self.processes, key=lambda x: x["arrival"])
        time = 0
        queue = []
        result = []
        total_wait = 0
        total_turnaround = 0
        remaining = {p["pid"]: p["burst"] for p in plist}
        arrived = []

        while plist or queue or any(remaining.values()):
            while plist and plist[0]["arrival"] <= time:
                arrived.append(plist.pop(0))
            queue += arrived
            arrived = []

            if queue:
                p = queue.pop(0)
                pid = p["pid"]
                start = time
                exec_time = min(quanta, remaining[pid])
                time += exec_time
                remaining[pid] -= exec_time

                while plist and plist[0]["arrival"] <= time:
                    queue.append(plist.pop(0))

                if remaining[pid] > 0:
                    queue.append(p)
                else:
                    finish = time
                    wait = finish - p["arrival"] - p["burst"]
                    turnaround = finish - p["arrival"]
                    total_wait += wait
                    total_turnaround += turnaround
                    result.append(f"{pid}: Finish={finish}, Wait={wait}, Turnaround={turnaround}")
            else:
                time += 1

        avg_wait = total_wait / len(self.processes)
        avg_turn = total_turnaround / len(self.processes)
        result.append(f"\nAvg Waiting Time: {avg_wait:.2f}")
        result.append(f"Avg Turnaround Time: {avg_turn:.2f}")
        return "\n".join(result)

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerApp(root)
    root.mainloop()
