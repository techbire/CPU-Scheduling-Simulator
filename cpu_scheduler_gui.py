import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('Agg')  # Set backend before other imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tabulate import tabulate
import numpy as np
import copy

plt.style.use('ggplot')

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1000x800")
        
        self.tasks = []
        self.current_id = 1
        self.current_figure = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Task Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Add Task", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Task ID:").grid(row=0, column=0, padx=2)
        self.task_id = ttk.Entry(input_frame, width=5)
        self.task_id.grid(row=0, column=1, padx=2)
        self.task_id.insert(0, "1")
        
        ttk.Label(input_frame, text="Arrival:").grid(row=0, column=2, padx=2)
        self.arrival_time = ttk.Entry(input_frame, width=5)
        self.arrival_time.grid(row=0, column=3, padx=2)
        
        ttk.Label(input_frame, text="Burst:").grid(row=0, column=4, padx=2)
        self.burst_time = ttk.Entry(input_frame, width=5)
        self.burst_time.grid(row=0, column=5, padx=2)
        
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=6, padx=2)
        self.priority = ttk.Entry(input_frame, width=5)
        self.priority.grid(row=0, column=7, padx=2)
        self.priority.grid_remove()

        self.add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        self.add_btn.grid(row=0, column=8, padx=10)

        # Task List Frame
        list_frame = ttk.LabelFrame(main_frame, text="Task List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ('ID', 'Arrival', 'Burst', 'Priority')
        self.task_list = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        for col in columns:
            self.task_list.heading(col, text=col)
            self.task_list.column(col, width=80, anchor=tk.CENTER)
        self.task_list.pack(fill=tk.BOTH, expand=True)

        # Algorithm Selection Frame
        algo_frame = ttk.LabelFrame(main_frame, text="Scheduling Algorithm", padding=10)
        algo_frame.pack(fill=tk.X, pady=5)
        
        self.algo_var = tk.StringVar()
        algorithms = [
            "First-Come, First-Served (FCFS)",
            "Shortest Job First (SJF)",
            "Priority (Non-Preemptive)",
            "Priority (Preemptive)",
            "Round Robin (RR)",
            "Shortest Remaining Time First (SRTF)"
        ]
        
        self.algo_menu = ttk.Combobox(algo_frame, textvariable=self.algo_var, values=algorithms, width=30)
        self.algo_menu.current(0)
        self.algo_menu.pack(side=tk.LEFT, padx=5)
        self.algo_menu.bind("<<ComboboxSelected>>", self.toggle_options)
        
        self.quantum_label = ttk.Label(algo_frame, text="Time Quantum:")
        self.quantum = ttk.Entry(algo_frame, width=5)
        self.quantum.insert(0, "2")
        self.quantum_label.pack(side=tk.LEFT, padx=5)
        self.quantum.pack(side=tk.LEFT, padx=5)
        self.quantum_label.pack_forget()
        self.quantum.pack_forget()

        self.simulate_btn = ttk.Button(algo_frame, text="Simulate", command=self.simulate)
        self.simulate_btn.pack(side=tk.RIGHT, padx=5)

        # Results and Gantt Frame
        results_gantt_frame = ttk.Frame(main_frame)
        results_gantt_frame.pack(fill=tk.BOTH, expand=True)

        # Results Frame
        results_frame = ttk.LabelFrame(results_gantt_frame, text="Results", padding=10)
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Gantt Chart Frame
        self.gantt_frame = ttk.LabelFrame(results_gantt_frame, text="Gantt Chart", padding=10)
        self.gantt_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def toggle_options(self, event=None):
        selected = self.algo_var.get()
        if "Round Robin" in selected:
            self.quantum_label.pack(side=tk.LEFT, padx=5)
            self.quantum.pack(side=tk.LEFT, padx=5)
            self.priority.grid_remove()
        elif "Priority" in selected:
            self.priority.grid()
            self.quantum_label.pack_forget()
            self.quantum.pack_forget()
        else:
            self.priority.grid_remove()
            self.quantum_label.pack_forget()
            self.quantum.pack_forget()

    def add_task(self):
        try:
            task_id = int(self.task_id.get())
            arrival = int(self.arrival_time.get())
            burst = int(self.burst_time.get())
            priority = int(self.priority.get()) if self.priority.grid_info() else 0
            
            if any(t['id'] == task_id for t in self.tasks):
                messagebox.showerror("Error", "Task ID must be unique!")
                return

            task = {
                'id': task_id,
                'arrival': arrival,
                'burst': burst,
                'priority': priority,
                'remaining': burst,
                'start': -1,
                'finish': -1,
                'response': -1
            }
            
            self.tasks.append(task)
            self.task_list.insert('', 'end', values=(task_id, arrival, burst, priority))
            
            self.current_id += 1
            self.task_id.delete(0, tk.END)
            self.task_id.insert(0, str(self.current_id))
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input values!")

    def simulate(self):
        if not self.tasks:
            messagebox.showerror("Error", "No tasks added!")
            return
            
        algorithm = self.algo_var.get()
        try:
            quantum = int(self.quantum.get()) if "Round Robin" in algorithm else 0
        except ValueError:
            messagebox.showerror("Error", "Invalid quantum value!")
            return

        # Run selected algorithm
        try:
            if "FCFS" in algorithm:
                result = self.fcfs(copy.deepcopy(self.tasks))
            elif "SJF" in algorithm:
                result = self.sjf(copy.deepcopy(self.tasks))
            elif "Priority (Non-Preemptive)" in algorithm:
                result = self.priority_non_preemptive(copy.deepcopy(self.tasks))
            elif "Priority (Preemptive)" in algorithm:
                result = self.priority_preemptive(copy.deepcopy(self.tasks))
            elif "Round Robin" in algorithm:
                result = self.round_robin(copy.deepcopy(self.tasks), quantum)
            elif "SRTF" in algorithm:
                result = self.srtf(copy.deepcopy(self.tasks))
        except Exception as e:
            messagebox.showerror("Simulation Error", str(e))
            return

        self.display_results(result['tasks'], result['gantt'])

    # Scheduling algorithms (same as before)
    def fcfs(self, tasks):
        tasks.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt = []
        
        for task in tasks:
            if current_time < task['arrival']:
                current_time = task['arrival']
            
            task['start'] = current_time
            task['response'] = current_time - task['arrival']
            gantt.append({'task': task['id'], 'start': current_time, 'end': current_time + task['burst']})
            
            current_time += task['burst']
            task['finish'] = current_time
            task['remaining'] = 0
            task['turnaround'] = task['finish'] - task['arrival']
            task['waiting'] = task['turnaround'] - task['burst']
        
        return {'tasks': tasks, 'gantt': gantt}
    
    def sjf(self, tasks):
        tasks.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt = []
        ready_queue = []
        i = 0
        n = len(tasks)
        
        while i < n or ready_queue:
            while i < n and tasks[i]['arrival'] <= current_time:
                ready_queue.append(tasks[i])
                i += 1
            
            if not ready_queue:
                current_time = tasks[i]['arrival']
                continue
                
            ready_queue.sort(key=lambda x: x['burst'])
            task = ready_queue.pop(0)
            
            if task['start'] == -1:
                task['start'] = current_time
                task['response'] = current_time - task['arrival']
            
            gantt.append({'task': task['id'], 'start': current_time, 'end': current_time + task['burst']})
            current_time += task['burst']
            task['finish'] = current_time
            task['remaining'] = 0
            task['turnaround'] = task['finish'] - task['arrival']
            task['waiting'] = task['turnaround'] - task['burst']
        
        return {'tasks': tasks, 'gantt': gantt}
    
    def priority_non_preemptive(self, tasks):
        tasks.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt = []
        ready_queue = []
        i = 0
        n = len(tasks)
        
        while i < n or ready_queue:
            while i < n and tasks[i]['arrival'] <= current_time:
                ready_queue.append(tasks[i])
                i += 1
            
            if not ready_queue:
                current_time = tasks[i]['arrival']
                continue
                
            ready_queue.sort(key=lambda x: x['priority'])
            task = ready_queue.pop(0)
            
            if task['start'] == -1:
                task['start'] = current_time
                task['response'] = current_time - task['arrival']
            
            gantt.append({'task': task['id'], 'start': current_time, 'end': current_time + task['burst']})
            current_time += task['burst']
            task['finish'] = current_time
            task['remaining'] = 0
            task['turnaround'] = task['finish'] - task['arrival']
            task['waiting'] = task['turnaround'] - task['burst']
        
        return {'tasks': tasks, 'gantt': gantt}
    
    def priority_preemptive(self, tasks):
        tasks.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt = []
        ready_queue = []
        i = 0
        n = len(tasks)
        prev_task = None
        
        for task in tasks:
            task['remaining'] = task['burst']
        
        while i < n or ready_queue:
            while i < n and tasks[i]['arrival'] <= current_time:
                ready_queue.append(tasks[i])
                i += 1
            
            if not ready_queue:
                current_time = tasks[i]['arrival']
                continue
                
            ready_queue.sort(key=lambda x: x['priority'])
            task = ready_queue[0]
            
            if prev_task and prev_task != task and prev_task['remaining'] > 0:
                gantt.append({'task': prev_task['id'], 'start': prev_task['start_time'], 'end': current_time})
            
            if prev_task != task:
                if task['start'] == -1:
                    task['start'] = current_time
                    task['response'] = current_time - task['arrival']
                task['start_time'] = current_time
            
            task['remaining'] -= 1
            current_time += 1
            prev_task = task
            
            if task['remaining'] == 0:
                ready_queue.pop(0)
                task['finish'] = current_time
                gantt.append({'task': task['id'], 'start': task['start_time'], 'end': current_time})
                task['turnaround'] = task['finish'] - task['arrival']
                task['waiting'] = task['turnaround'] - task['burst']
        
        return {'tasks': tasks, 'gantt': gantt}
    
    def round_robin(self, tasks, quantum):
        tasks.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt = []
        ready_queue = []
        i = 0
        n = len(tasks)
        
        for task in tasks:
            task['remaining'] = task['burst']
        
        while i < n or ready_queue:
            while i < n and tasks[i]['arrival'] <= current_time:
                ready_queue.append(tasks[i])
                i += 1
            
            if not ready_queue:
                current_time = tasks[i]['arrival']
                continue
                
            task = ready_queue.pop(0)
            
            if task['start'] == -1:
                task['start'] = current_time
                task['response'] = current_time - task['arrival']
            
            exec_time = min(quantum, task['remaining'])
            gantt.append({'task': task['id'], 'start': current_time, 'end': current_time + exec_time})
            
            current_time += exec_time
            task['remaining'] -= exec_time
            
            while i < n and tasks[i]['arrival'] <= current_time:
                ready_queue.append(tasks[i])
                i += 1
                
            if task['remaining'] > 0:
                ready_queue.append(task)
            else:
                task['finish'] = current_time
                task['turnaround'] = task['finish'] - task['arrival']
                task['waiting'] = task['turnaround'] - task['burst']
        
        return {'tasks': tasks, 'gantt': gantt}
    
    def srtf(self, tasks):
        tasks.sort(key=lambda x: x['arrival'])
        current_time = 0
        gantt = []
        ready_queue = []
        i = 0
        n = len(tasks)
        prev_task = None
        
        for task in tasks:
            task['remaining'] = task['burst']
        
        while i < n or ready_queue:
            while i < n and tasks[i]['arrival'] <= current_time:
                ready_queue.append(tasks[i])
                i += 1
            
            if not ready_queue:
                current_time = tasks[i]['arrival']
                continue
                
            ready_queue.sort(key=lambda x: x['remaining'])
            task = ready_queue[0]
            
            if prev_task and prev_task != task and prev_task['remaining'] > 0:
                gantt.append({'task': prev_task['id'], 'start': prev_task['start_time'], 'end': current_time})
            
            if prev_task != task:
                if task['start'] == -1:
                    task['start'] = current_time
                    task['response'] = current_time - task['arrival']
                task['start_time'] = current_time
            
            task['remaining'] -= 1
            current_time += 1
            prev_task = task
            
            if task['remaining'] == 0:
                ready_queue.pop(0)
                task['finish'] = current_time
                gantt.append({'task': task['id'], 'start': task['start_time'], 'end': current_time})
                task['turnaround'] = task['finish'] - task['arrival']
                task['waiting'] = task['turnaround'] - task['burst']
        
        return {'tasks': tasks, 'gantt': gantt}
    

    def display_results(self, tasks, gantt):
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        if not tasks:
            messagebox.showerror("Error", "No results to display!")
            return

        # Calculate metrics
        total_waiting = sum(t['waiting'] for t in tasks)
        total_turnaround = sum(t['turnaround'] for t in tasks)
        total_response = sum(t['response'] for t in tasks)
        n = len(tasks)
        completion_time = max(t['finish'] for t in tasks) if tasks else 0

        # Prepare results text
        results_text = "SCHEDULING RESULTS\n" + "="*50 + "\n"
        results_text += tabulate(
            [
                [t['id'], t['arrival'], t['burst'], t['priority'],
                 t['start'], t['finish'], t['turnaround'],
                 t['waiting'], t['response']] for t in tasks
            ],
            headers=['ID', 'Arrival', 'Burst', 'Priority', 'Start', 'Finish', 
                    'Turnaround', 'Waiting', 'Response'],
            tablefmt='grid'
        )
        
        results_text += "\n\nPERFORMANCE METRICS\n" + "="*50 + "\n"
        results_text += f"Average Waiting Time: {total_waiting/n:.2f}\n"
        results_text += f"Average Turnaround Time: {total_turnaround/n:.2f}\n"
        results_text += f"Average Response Time: {total_response/n:.2f}\n"
        results_text += f"Throughput: {n/completion_time:.2f} processes/unit time\n"

        self.results_text.insert(tk.END, results_text)
        
        # Update Gantt chart
        self.update_gantt_chart(gantt)

    def update_gantt_chart(self, gantt):
        # Clear previous chart
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()

        if not gantt:
            empty_label = ttk.Label(self.gantt_frame, text="No Gantt chart available")
            empty_label.pack(expand=True)
            return

        # Create new figure
        fig = plt.figure(figsize=(10, 3))
        ax = fig.add_subplot(111)

        # Create color mapping
        unique_tasks = list({entry['task'] for entry in gantt})
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_tasks)))
        color_map = {task: colors[i] for i, task in enumerate(unique_tasks)}

        # Plot Gantt chart
        for i, entry in enumerate(gantt):
            start = entry['start']
            duration = entry['end'] - entry['start']
            ax.broken_barh([(start, duration)], (0.1, 0.8),
                          facecolors=color_map[entry['task']],
                          edgecolor='black',
                          linewidth=0.5)
            
            # Add task label
            ax.text(start + duration/2, 0.5, f"P{entry['task']}",
                   ha='center', va='center', color='white', fontsize=8)
            
            # Add time markers
            if i == 0:
                ax.text(start, -0.2, str(start), ha='left', va='top', fontsize=8)
            ax.text(entry['end'], -0.2, str(entry['end']), ha='right', va='top', fontsize=8)

        # Format chart
        ax.set_yticks([])
        ax.set_xlabel('Time Units')
        ax.set_title('Gantt Chart')
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # Set axis limits
        max_time = gantt[-1]['end']
        ax.set_xlim(0, max_time * 1.05)
        ax.set_ylim(0, 1)
        
        # Add legend
        legend_handles = [plt.Rectangle((0,0),1,1, fc=color_map[task]) 
                        for task in unique_tasks]
        ax.legend(legend_handles, [f'P{task}' for task in unique_tasks],
                 loc='upper right', fontsize=8)

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()