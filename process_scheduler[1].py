import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = -1
        self.completion_time = 0

class ProcessSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduler Simulator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.processes = []
        self.priority_type = tk.IntVar(value=1) 
        self.create_widgets()
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('ProcessList.Treeview', font=('Helvetica', 9), rowheight=25)
        self.style.map('TButton',
                      foreground=[('active', 'black'), ('!active', 'black')],
                      background=[('active', '#d9d9d9'), ('!active', '#e6e6e6')])
        
    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=(10, 5))
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Right panel - Output
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding=(10, 5))
        self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        self.add_btn = ttk.Button(self.control_frame, text="Add Process", command=self.add_process)
        self.add_btn.pack(fill=tk.X, pady=5)
        
        self.clear_btn = ttk.Button(self.control_frame, text="Clear All Processes", command=self.clear_processes)
        self.clear_btn.pack(fill=tk.X, pady=5)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Priority range settings
        ttk.Label(self.control_frame, text="Custom Priority Range", style='Header.TLabel').pack(pady=5)
        
        ttk.Label(self.control_frame, text="High Priority Value").pack()
        self.high_priority_entry = ttk.Entry(self.control_frame)
        self.high_priority_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="Low Priority Value").pack()
        self.low_priority_entry = ttk.Entry(self.control_frame)
        self.low_priority_entry.pack(fill=tk.X, pady=2)
        
        self.set_priority_range_btn = ttk.Button(self.control_frame, text="Set Priority Range", command=self.set_priority_range)
        self.set_priority_range_btn.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.control_frame, text="Scheduling Algorithms", style='Header.TLabel').pack(pady=5)
        
        self.fcfs_btn = ttk.Button(self.control_frame, text="Run FCFS", command=self.run_fcfs)
        self.fcfs_btn.pack(fill=tk.X, pady=5)
        
        self.sjf_btn = ttk.Button(self.control_frame, text="Run SJF", command=self.run_sjf)
        self.sjf_btn.pack(fill=tk.X, pady=5)
        
        self.priority_btn = ttk.Button(self.control_frame, text="Run Priority Scheduling", command=self.run_priority)
        self.priority_btn.pack(fill=tk.X, pady=5)
        
        self.rr_btn = ttk.Button(self.control_frame, text="Run Round Robin", command=self.run_rr)
        self.rr_btn.pack(fill=tk.X, pady=5)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.analyze_button = ttk.Button(self.control_frame, text="Analyze Best Algorithm", command=self.analyze_best_algorithm)
        self.analyze_button.pack(fill=tk.X, pady=5)
        
        self.exit_btn = ttk.Button(self.control_frame, text="Exit", command=self.root.destroy)
        self.exit_btn.pack(fill=tk.X, pady=5)

        # Process list display
        self.process_list_frame = ttk.LabelFrame(self.output_frame, text="Process List")
        self.process_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(self.process_list_frame, columns=('PID', 'Arrival', 'Burst', 'Priority'), 
                                show='headings', style='ProcessList.Treeview')
        
        self.tree.heading('PID', text='Process ID')
        self.tree.heading('Arrival', text='Arrival Time')
        self.tree.heading('Burst', text='Burst Time')
        self.tree.heading('Priority', text='Priority')
        
        self.tree.column('PID', width=100, anchor=tk.CENTER)
        self.tree.column('Arrival', width=100, anchor=tk.CENTER)
        self.tree.column('Burst', width=100, anchor=tk.CENTER)
        self.tree.column('Priority', width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Metrics display
        self.metrics_frame = ttk.LabelFrame(self.output_frame, text="Metrics")
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.metrics_text = scrolledtext.ScrolledText(self.metrics_frame, wrap=tk.WORD, width=60, height=10)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Gantt chart frame
        self.gantt_frame = ttk.LabelFrame(self.output_frame, text="Gantt Chart")
        self.gantt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize empty figure for Gantt chart
        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.gantt_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def add_process(self):
        
        pid = simpledialog.askstring("Add Process", "Enter Process ID:")
        
        if not pid or not pid.strip():
            messagebox.showerror("Error", "Process ID cannot be empty.")
            return
        if not pid.isdigit():
            messagebox.showerror("Error", "Process ID must be a number.")
            return
        if any(p.pid == pid for p in self.processes):
            messagebox.showerror("Error", "Process ID must be unique.")
            return

        arrival = simpledialog.askinteger("Add Process", "Enter Arrival Time (>= 0):", minvalue=0)
        if arrival is None:
            return
            
        burst = simpledialog.askinteger("Add Process",  "Enter Burst Time (> 0):", minvalue=1)
        if burst is None:
            return
            
        priority = simpledialog.askinteger("Add Process", "Enter Priority:", initialvalue=0)
        if priority is None:
            priority = 0
        
        if arrival < 0:
            messagebox.showerror("Error", "Arrival time must be non-negative.")
            return
        if burst <= 0:
            messagebox.showerror("Error", "Burst time must be greater than zero.")
            return
        if priority < 0:
            messagebox.showerror("Error", "Priority must be non-negative.")
            return
    
        self.processes.append(Process(pid, arrival, burst, priority))
        self.update_process_list()
        messagebox.showinfo("Success", f"Process {pid} added successfully.")
        
    def set_global_priority(self):
        """ Set the global priority before scheduling any process. """
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule!")
            return
        
        # Prompt user to set priority scheme globally before scheduling
        user_choice = messagebox.askyesno("Set Global Priority", "Would you like to set priority: Lower value = Higher priority?")
        
        # Update global priority type based on user selection
        self.priority_type.set(1 if user_choice else 0)
    def clear_processes(self):
        self.processes = []
        self.update_process_list()
        self.clear_metrics()
        self.clear_gantt_chart()
        messagebox.showinfo("Cleared", "All processes cleared.")
        
    def set_priority_range(self):
        try:
            high = int(self.high_priority_entry.get())
            low = int(self.low_priority_entry.get())
            if high == low:
                raise ValueError("High and Low priority values cannot be the same.")
            self.priority_type.set(1 if high < low else 0)  # 1 = lower number = higher priority
            messagebox.showinfo("Priority Set", f"Priority direction set: {high} (High) to {low} (Low)")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid integer values for priority range.\n{e}")
    
        
    def update_process_list(self):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items
        for p in self.processes:
            self.tree.insert('', tk.END, values=(p.pid, p.arrival_time, p.burst_time, p.priority))
            
    def clear_metrics(self):
        self.metrics_text.delete(1.0, tk.END)
        
    def clear_gantt_chart(self):
        self.ax.clear()
        self.ax.set_title("No data available")
        self.canvas.draw()
        
    def display_metrics(self, processes):
        self.clear_metrics()
        output = "\nPID\tArrival\tBurst\tStart\tCompletion\tTurnaround\tWaiting\n"
        total_tat = total_wt = 0
        
        for p in processes:
            turnaround = p.completion_time - p.arrival_time
            waiting = turnaround - p.burst_time
            total_tat += turnaround
            total_wt += waiting
            output += (f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.start_time}\t"
                      f"{p.completion_time}\t\t{turnaround}\t\t{waiting}\n")
            
        n = len(processes)
        output += f"\nAverage Turnaround Time: {total_tat/n:.2f}\n"
        output += f"Average Waiting Time: {total_wt/n:.2f}\n"
        
        self.metrics_text.insert(tk.END, output)
        
    def show_gantt_chart(self, processes):
        self.ax.clear()
        
        if not processes:
            self.ax.set_title("No processes to display")
            self.canvas.draw()
            return
            
        self.ax.set_title("Gantt Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Processes")
        self.ax.set_yticks([10 * i for i in range(1, len(processes)+1)])
        self.ax.set_yticklabels([p.pid for p in processes])
        self.ax.grid(True)

        for i, p in enumerate(processes):
            self.ax.broken_barh([(p.start_time, p.burst_time)], (10 * (i+1)-5, 9), 
                               facecolors=('tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple')[i%5])

        self.canvas.draw()
        
    def calculate_metrics(self, processes):
        n = len(processes)
        tat_total = wt_total = rt_total = 0

        for p in processes:
            turnaround = p.completion_time - p.arrival_time
            waiting = turnaround - p.burst_time
            response = p.start_time - p.arrival_time

            tat_total += turnaround
            wt_total += waiting
            rt_total += response

        return {
            'TAT': tat_total / n,
            'WT': wt_total / n,
            'RT': rt_total / n
        }

    def run_fcfs(self, simulate_only=False):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule!")
            return
            
        processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
        processes_copy.sort(key=lambda x: x.arrival_time)
        time = 0
        
        for p in processes_copy:
            if time < p.arrival_time:
                time = p.arrival_time
            p.start_time = time
            time += p.burst_time
            p.completion_time = time
        if simulate_only:
            return self.calculate_metrics(processes_copy)
        else:
            self.display_metrics(processes_copy)
            self.show_gantt_chart(processes_copy)    
        
    def run_sjf(self, simulate_only=False):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule!")
            return
            
        processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
        time = 0
        completed = 0
        n = len(processes_copy)
        ready_queue = []

        while completed < n:
            for p in processes_copy:
                if p.arrival_time <= time and p not in ready_queue and p.completion_time == 0:
                    ready_queue.append(p)

            if ready_queue:
                ready_queue.sort(key=lambda x: x.burst_time)
                current = ready_queue.pop(0)
                if time < current.arrival_time:
                    time = current.arrival_time
                current.start_time = time
                time += current.burst_time
                current.completion_time = time
                completed += 1
            else:
                time += 1

        if simulate_only:
            return self.calculate_metrics(processes_copy)
        else:        
            self.display_metrics(processes_copy)
            self.show_gantt_chart(processes_copy)

    def run_priority(self,  simulate_only=False):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule!")
            return
            
        processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
        time = 0
        completed = 0
        n = len(processes_copy)
        ready_queue = []

        while completed < n:
            for p in processes_copy:
                if p.arrival_time <= time and p not in ready_queue and p.completion_time == 0:
                    ready_queue.append(p)

            if ready_queue:
                if self.priority_type.get() == 1:
                    ready_queue.sort(key=lambda x: (x.priority, x.arrival_time))  # Lower = higher
                else:
                    ready_queue.sort(key=lambda x: (-x.priority, x.arrival_time)) 
                current = ready_queue.pop(0)
                if time < current.arrival_time:
                    time = current.arrival_time
                current.start_time = time
                time += current.burst_time
                current.completion_time = time
                completed += 1
            else:
                time += 1
        if simulate_only:
            return self.calculate_metrics(processes_copy)
        else:         
            self.display_metrics(processes_copy)
            self.show_gantt_chart(processes_copy)
    
    def run_rr(self, simulate_only=False):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule!")
            return
            
        quantum = simpledialog.askinteger("Round Robin", "Enter Time Quantum (> 0):", initialvalue=2)
        if quantum is None:
            return
        if quantum <= 0:
            messagebox.showerror("Error", "Time quantum must be greater than zero.")
            return    
        processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
        time = 0
        queue = []
        n = len(processes_copy)
        completed = 0
        i = 0
        processes_copy.sort(key=lambda x: x.arrival_time)
        queue.append(processes_copy[0])
        i = 1

        while completed < n:
            if queue:
                current = queue.pop(0)
                if current.start_time == -1:
                    current.start_time = time
                if current.remaining_time <= quantum:
                    time += current.remaining_time
                    current.remaining_time = 0
                    current.completion_time = time
                    completed += 1
                else:
                    time += quantum
                    current.remaining_time -= quantum

                while i < n and processes_copy[i].arrival_time <= time:
                    queue.append(processes_copy[i])
                    i += 1

                if current.remaining_time > 0:
                    queue.append(current)
            else:
                if i < n:
                    queue.append(processes_copy[i])
                    time = processes_copy[i].arrival_time
                    i += 1
        if simulate_only:
            return self.calculate_metrics(processes_copy)
        else:             
            self.display_metrics(processes_copy)
            self.show_gantt_chart(processes_copy)

    
    def analyze_best_algorithm(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to analyze!")
            return

        results = []

        algos = [
            (self.run_fcfs, "FCFS"),
            (self.run_sjf, "SJF"),
            (self.run_priority, "Priority"),
            (self.run_rr, "Round Robin")
        ]

        for func, name in algos:
            try:
                metrics = func(simulate_only=True)
                if metrics:
                    results.append((name, metrics))
            except Exception as e:
                print(f"Error in {name}: {e}")

        # Determine best based on WT (or TAT if preferred)
        best_algo = min(results, key=lambda x: x[1]['WT'])[0]

        # Show comparison
        output = "Algorithm Comparison:\n"
        output += f"{'Algorithm':<15}{'Avg TAT':<15}{'Avg WT':<15}{'Avg RT':<15}\n"
        for name, metric in results:
            output += f"{name:<15}{metric['TAT']:<15.2f}{metric['WT']:<15.2f}{metric['RT']:<15.2f}\n"

        output += f"\nBest Algorithm (Lowest Avg WT): {best_algo}\n"

        self.clear_metrics()
        self.metrics_text.insert(tk.END, output)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulerApp(root)
    root.mainloop()