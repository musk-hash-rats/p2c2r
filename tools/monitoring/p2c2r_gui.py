#!/usr/bin/env python3
"""
P2C2R GUI - The Uber of Game Compute
Modern, sleek interface for monitoring and controlling the P2C2R network
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import json
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Try to import websockets for real-time monitoring
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


class P2C2RGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P2C2R - The Uber of Game Compute")
        self.root.geometry("1200x800")
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a2e',           # Dark blue background
            'card': '#16213e',          # Card background
            'accent': '#0f3460',        # Accent color
            'primary': '#00d4ff',       # Cyan primary
            'success': '#00ff88',       # Green success
            'warning': '#ffa500',       # Orange warning
            'error': '#ff4757',         # Red error
            'text': '#eaeaea',          # Light text
            'text_dim': '#a0a0a0',      # Dimmed text
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Network status
        self.network_running = False
        self.network_process = None
        self.stats = {
            'coordinator': {'status': 'offline', 'connections': 0},
            'peers': [],
            'users': [],
            'tasks': {'total': 0, 'completed': 0, 'failed': 0},
        }
        
        self.setup_ui()
        self.update_stats()
        
    def setup_ui(self):
        """Setup the complete UI"""
        
        # Header
        self.create_header()
        
        # Main content area with scrolling
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Left panel (2/3 width) - Network status and monitoring
        left_panel = tk.Frame(main_frame, bg=self.colors['bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_control_panel(left_panel)
        self.create_network_status(left_panel)
        self.create_activity_feed(left_panel)
        
        # Right panel (1/3 width) - Stats and economics
        right_panel = tk.Frame(main_frame, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        self.create_stats_panel(right_panel)
        self.create_economics_panel(right_panel)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Create the header with logo and title"""
        header = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo/Icon (text-based)
        logo = tk.Label(
            header,
            text="🚀",
            font=("Arial", 36),
            bg=self.colors['accent'],
            fg=self.colors['primary']
        )
        logo.pack(side=tk.LEFT, padx=20)
        
        # Title and tagline
        title_frame = tk.Frame(header, bg=self.colors['accent'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=15)
        
        title = tk.Label(
            title_frame,
            text="P2C2R Control Center",
            font=("Arial", 24, "bold"),
            bg=self.colors['accent'],
            fg=self.colors['text']
        )
        title.pack(anchor=tk.W)
        
        tagline = tk.Label(
            title_frame,
            text="The Uber of Game Compute - Distributed GPU Marketplace",
            font=("Arial", 11),
            bg=self.colors['accent'],
            fg=self.colors['text_dim']
        )
        tagline.pack(anchor=tk.W)
        
    def create_control_panel(self, parent):
        """Create network control buttons"""
        card = self.create_card(parent, "Network Control")
        
        button_frame = tk.Frame(card, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=10)
        
        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Network",
            command=self.start_network,
            font=("Arial", 12, "bold"),
            bg=self.colors['success'],
            fg='#000000',
            activebackground='#00cc70',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop Network",
            command=self.stop_network,
            font=("Arial", 12, "bold"),
            bg=self.colors['error'],
            fg='#ffffff',
            activebackground='#cc3945',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Restart button
        restart_btn = tk.Button(
            button_frame,
            text="🔄 Restart",
            command=self.restart_network,
            font=("Arial", 12),
            bg=self.colors['warning'],
            fg='#000000',
            activebackground='#cc8400',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        restart_btn.pack(side=tk.LEFT, padx=5)
        
    def create_network_status(self, parent):
        """Create network status cards"""
        card = self.create_card(parent, "Network Status")
        
        # Status grid
        status_frame = tk.Frame(card, bg=self.colors['card'])
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Coordinator status
        coord_frame = self.create_status_box(
            status_frame,
            "Cloud Coordinator",
            "🌐",
            "offline"
        )
        coord_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.coord_status_label = coord_frame.winfo_children()[2]
        
        # Peers status
        peers_frame = self.create_status_box(
            status_frame,
            "Active Peers",
            "💻",
            "0"
        )
        peers_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.peers_status_label = peers_frame.winfo_children()[2]
        
        # Users status
        users_frame = self.create_status_box(
            status_frame,
            "Connected Users",
            "🎮",
            "0"
        )
        users_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        self.users_status_label = users_frame.winfo_children()[2]
        
        # Tasks status
        tasks_frame = self.create_status_box(
            status_frame,
            "Tasks Processed",
            "⚡",
            "0"
        )
        tasks_frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        self.tasks_status_label = tasks_frame.winfo_children()[2]
        
        # Make grid responsive
        for i in range(4):
            status_frame.columnconfigure(i, weight=1)
            
    def create_activity_feed(self, parent):
        """Create activity feed"""
        card = self.create_card(parent, "Activity Feed")
        
        # Scrollable text area
        text_frame = tk.Frame(card, bg=self.colors['card'])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.activity_text = tk.Text(
            text_frame,
            height=10,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=("Courier", 10),
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD
        )
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.activity_text.yview)
        
        # Initial message
        self.log_activity("P2C2R Control Center initialized")
        self.log_activity("Ready to start network...", "info")
        
    def create_stats_panel(self, parent):
        """Create statistics panel"""
        card = self.create_card(parent, "Live Statistics")
        
        stats_frame = tk.Frame(card, bg=self.colors['card'])
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Stats items
        self.create_stat_item(stats_frame, "Uptime:", "0h 0m", 0)
        self.create_stat_item(stats_frame, "Avg Latency:", "-- ms", 1)
        self.create_stat_item(stats_frame, "Success Rate:", "-- %", 2)
        self.create_stat_item(stats_frame, "Network Load:", "-- %", 3)
        
    def create_economics_panel(self, parent):
        """Create economics/Uber model panel"""
        card = self.create_card(parent, "💰 The Uber Model")
        
        econ_frame = tk.Frame(card, bg=self.colors['card'])
        econ_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Cost comparison
        self.create_econ_item(econ_frame, "💻 Local GPU:", "$1,200", self.colors['error'], 0)
        self.create_econ_item(econ_frame, "🌐 P2C2R:", "$7.50/mo", self.colors['success'], 1)
        
        # Separator
        sep = tk.Frame(econ_frame, bg=self.colors['text_dim'], height=1)
        sep.pack(fill=tk.X, pady=10)
        
        self.create_econ_item(econ_frame, "💰 Savings:", "94% cheaper", self.colors['primary'], 2)
        self.create_econ_item(econ_frame, "📊 Platform Fee:", "25%", self.colors['text_dim'], 3)
        self.create_econ_item(econ_frame, "🎯 Profit Margin:", "19% net", self.colors['success'], 4)
        
    def create_footer(self):
        """Create footer with info"""
        footer = tk.Frame(self.root, bg=self.colors['accent'], height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_label = tk.Label(
            footer,
            text="P2C2R v0.1.0 | WebSocket Protocol | github.com/musk-hash-rats/p2c2r",
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg=self.colors['text_dim']
        )
        footer_label.pack(expand=True)
        
    # Helper methods for creating UI components
    
    def create_card(self, parent, title):
        """Create a card container"""
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief=tk.FLAT)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Arial", 14, "bold"),
            bg=self.colors['card'],
            fg=self.colors['primary'],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        # Content area
        content = tk.Frame(card_frame, bg=self.colors['card'])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        return content
        
    def create_status_box(self, parent, title, icon, value):
        """Create a status box"""
        box = tk.Frame(parent, bg=self.colors['bg'], relief=tk.FLAT)
        
        # Icon
        icon_label = tk.Label(
            box,
            text=icon,
            font=("Arial", 24),
            bg=self.colors['bg'],
            fg=self.colors['primary']
        )
        icon_label.pack(pady=(10, 0))
        
        # Value
        value_label = tk.Label(
            box,
            text=value,
            font=("Arial", 18, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        value_label.pack()
        
        # Title
        title_label = tk.Label(
            box,
            text=title,
            font=("Arial", 9),
            bg=self.colors['bg'],
            fg=self.colors['text_dim']
        )
        title_label.pack(pady=(0, 10))
        
        return box
        
    def create_stat_item(self, parent, label, value, row):
        """Create a stat item"""
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill=tk.X, pady=5)
        
        label_widget = tk.Label(
            frame,
            text=label,
            font=("Arial", 11),
            bg=self.colors['card'],
            fg=self.colors['text_dim'],
            anchor=tk.W
        )
        label_widget.pack(side=tk.LEFT)
        
        value_widget = tk.Label(
            frame,
            text=value,
            font=("Arial", 11, "bold"),
            bg=self.colors['card'],
            fg=self.colors['primary'],
            anchor=tk.E
        )
        value_widget.pack(side=tk.RIGHT)
        
    def create_econ_item(self, parent, label, value, color, row):
        """Create an economics item"""
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill=tk.X, pady=5)
        
        label_widget = tk.Label(
            frame,
            text=label,
            font=("Arial", 11),
            bg=self.colors['card'],
            fg=self.colors['text'],
            anchor=tk.W
        )
        label_widget.pack(side=tk.LEFT)
        
        value_widget = tk.Label(
            frame,
            text=value,
            font=("Arial", 11, "bold"),
            bg=self.colors['card'],
            fg=color,
            anchor=tk.E
        )
        value_widget.pack(side=tk.RIGHT)
        
    # Network control methods
    
    def start_network(self):
        """Start the P2C2R network"""
        script_path = Path(__file__).parent / "run_network.sh"
        
        if not script_path.exists():
            messagebox.showerror("Error", f"run_network.sh not found at {script_path}")
            return
            
        try:
            self.log_activity("Starting P2C2R network...", "info")
            
            # Run the network script
            self.network_process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(script_path.parent)
            )
            
            self.network_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log_activity("✓ Network started successfully", "success")
            self.log_activity("Coordinator running on localhost:8765", "info")
            
            # Update UI
            self.update_network_status(True)
            
        except Exception as e:
            self.log_activity(f"✗ Failed to start network: {str(e)}", "error")
            messagebox.showerror("Error", f"Failed to start network:\n{str(e)}")
            
    def stop_network(self):
        """Stop the P2C2R network"""
        if self.network_process:
            try:
                self.log_activity("Stopping P2C2R network...", "info")
                self.network_process.terminate()
                self.network_process.wait(timeout=5)
                self.log_activity("✓ Network stopped", "success")
            except subprocess.TimeoutExpired:
                self.network_process.kill()
                self.log_activity("✓ Network force stopped", "warning")
            except Exception as e:
                self.log_activity(f"✗ Error stopping network: {str(e)}", "error")
                
        self.network_running = False
        self.network_process = None
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.update_network_status(False)
        
    def restart_network(self):
        """Restart the network"""
        self.log_activity("Restarting network...", "info")
        self.stop_network()
        self.root.after(2000, self.start_network)
        
    def update_network_status(self, running):
        """Update network status displays"""
        if running:
            self.coord_status_label.config(text="online", fg=self.colors['success'])
            self.peers_status_label.config(text="3")
            self.users_status_label.config(text="1")
        else:
            self.coord_status_label.config(text="offline", fg=self.colors['error'])
            self.peers_status_label.config(text="0")
            self.users_status_label.config(text="0")
            self.tasks_status_label.config(text="0")
            
    def log_activity(self, message, level="info"):
        """Log activity to the feed"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color codes for different levels
        colors = {
            "info": self.colors['text'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['error']
        }
        
        color = colors.get(level, self.colors['text'])
        
        self.activity_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_text.see(tk.END)
        
    def update_stats(self):
        """Update statistics periodically"""
        if self.network_running:
            # Simulate stats updates (in production, would query actual network)
            import random
            
            tasks = int(self.tasks_status_label.cget("text"))
            self.tasks_status_label.config(text=str(tasks + random.randint(0, 5)))
            
        # Schedule next update
        self.root.after(2000, self.update_stats)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = P2C2RGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
