import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from PIL import Image, ImageTk
import os
import datetime
import random

class ModernChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Chat Application")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)
        self.root.configure(bg="#e6ebf5")
        
        # Load and store images
        self.images = {}
        self.load_images()
        
        # Create the main frames
        self.create_main_layout()
        
        # Populate with sample data
        self.populate_sample_data()
        
        # Set up bindings
        self.setup_bindings()
        
    def load_images(self):
        # Create a directory for icons if it doesn't exist
        if not os.path.exists("icons"):
            os.makedirs("icons")
            print("Created 'icons' directory. Please add your icon images there.")
        
        # Define default icons with their corresponding colors
        default_icons = {
            "profile": "#2979ff",
            "chat": "#2979ff",
            "send": "#2979ff",
            "archive": "#2979ff",
            "settings": "#2979ff",
            "more": "#2979ff",
            "attach": "#9e9e9e",
            "image": "#9e9e9e",
            "mic": "#9e9e9e",
            "add": "#2979ff",
            "menu": "#9e9e9e",
            "call": "#9e9e9e",
            "video": "#9e9e9e",
            "star": "#ffc107",
            "star_empty": "#e0e0e0"
        }
        
        # Try to load images, create colored rectangles if files don't exist
        for name, color in default_icons.items():
            try:
                img = Image.open(f"icons/{name}.png")
                self.images[name] = ImageTk.PhotoImage(img)
            except:
                # Create a colored rectangle as placeholder
                img = Image.new('RGB', (24, 24), color)
                self.images[name] = ImageTk.PhotoImage(img)
    
    def create_main_layout(self):
        # Main container frame
        self.main_frame = tk.Frame(self.root, bg="#e6ebf5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a content frame with white background and rounded corners (simulated with padding)
        self.content_frame = tk.Frame(self.main_frame, bg="white", bd=0, relief=tk.SOLID)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar (blue with icons)
        self.left_sidebar = tk.Frame(self.content_frame, width=70, bg="#2979ff")
        self.left_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.left_sidebar.pack_propagate(False)
        
        # Add sidebar icons
        self.create_sidebar_icons()
        
        # Conversation list frame
        self.conversations_frame = tk.Frame(self.content_frame, width=300, bg="white", bd=1, relief=tk.SOLID)
        self.conversations_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.conversations_frame.pack_propagate(False)
        
        # Create conversation list
        self.create_conversation_list()
        
        # Chat area frame
        self.chat_frame = tk.Frame(self.content_frame, bg="white")
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create chat area
        self.create_chat_area()
    
    def create_sidebar_icons(self):
        # Profile icon at top
        profile_btn = tk.Button(self.left_sidebar, image=self.images["profile"], bg="#2979ff", 
                               activebackground="#1565c0", bd=0, relief=tk.FLAT)
        profile_btn.pack(pady=(20, 30))
        
        # Chat icon (selected)
        chat_frame = tk.Frame(self.left_sidebar, bg="white", width=4, height=40)
        chat_frame.place(x=0, y=100)
        
        chat_btn = tk.Button(self.left_sidebar, image=self.images["chat"], bg="#2979ff", 
                             activebackground="#1565c0", bd=0, relief=tk.FLAT)
        chat_btn.pack(pady=10)
        
        # Other sidebar icons
        send_btn = tk.Button(self.left_sidebar, image=self.images["send"], bg="#2979ff", 
                            activebackground="#1565c0", bd=0, relief=tk.FLAT)
        send_btn.pack(pady=10)
        
        archive_btn = tk.Button(self.left_sidebar, image=self.images["archive"], bg="#2979ff", 
                               activebackground="#1565c0", bd=0, relief=tk.FLAT)
        archive_btn.pack(pady=10)
        
        # Settings at bottom
        settings_btn = tk.Button(self.left_sidebar, image=self.images["settings"], bg="#2979ff", 
                                activebackground="#1565c0", bd=0, relief=tk.FLAT)
        settings_btn.pack(side=tk.BOTTOM, pady=20)
        
        more_btn = tk.Button(self.left_sidebar, image=self.images["more"], bg="#2979ff", 
                            activebackground="#1565c0", bd=0, relief=tk.FLAT)
        more_btn.pack(side=tk.BOTTOM, pady=10)
    
    def create_conversation_list(self):
        # Search bar
        search_frame = tk.Frame(self.conversations_frame, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        search_icon = tk.Label(search_frame, image=self.images.get("search", self.images["more"]), bg="white")
        search_icon.pack(side=tk.LEFT, padx=(5, 0))
        
        search_entry = tk.Entry(search_frame, bd=0, bg="#f5f5f5", relief=tk.FLAT)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=5)
        search_entry.insert(0, "Search")
        
        # Conversations list canvas with scrollbar
        self.convo_canvas = tk.Canvas(self.conversations_frame, bg="white", bd=0, 
                                      highlightthickness=0)
        scrollbar = tk.Scrollbar(self.conversations_frame, orient=tk.VERTICAL, 
                                command=self.convo_canvas.yview)
        
        self.convo_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.convo_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for conversations
        self.convo_list_frame = tk.Frame(self.convo_canvas, bg="white")
        self.convo_canvas.create_window((0, 0), window=self.convo_list_frame, anchor="nw")
        
        # New conversation button
        new_convo_btn = tk.Button(self.conversations_frame, image=self.images["add"], bg="#2979ff", 
                                 activebackground="#1565c0", bd=0, relief=tk.FLAT,
                                 width=50, height=50, borderwidth=0)
        new_convo_btn.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")
        
        # Update canvas scroll region when frame size changes
        self.convo_list_frame.bind("<Configure>", lambda e: self.convo_canvas.configure(
            scrollregion=self.convo_canvas.bbox("all")))
    
    def create_chat_area(self):
        # Chat header
        chat_header = tk.Frame(self.chat_frame, bg="white", height=60, bd=0, relief=tk.SOLID)
        chat_header.pack(fill=tk.X)
        chat_header.pack_propagate(False)
        
        # User info in header
        self.header_profile = tk.Label(chat_header, image=self.images["profile"], bg="white")
        self.header_profile.pack(side=tk.LEFT, padx=10)
        
        header_info = tk.Frame(chat_header, bg="white")
        header_info.pack(side=tk.LEFT, fill=tk.Y)
        
        self.header_name = tk.Label(header_info, text="Jessica Carroll", font=("Segoe UI", 12, "bold"), bg="white")
        self.header_name.pack(anchor="w")
        
        self.header_status = tk.Label(header_info, text="Online", font=("Segoe UI", 9), fg="#4caf50", bg="white")
        self.header_status.pack(anchor="w")
        
        # Header action buttons
        header_actions = tk.Frame(chat_header, bg="white")
        header_actions.pack(side=tk.RIGHT, padx=10)
        
        call_btn = tk.Button(header_actions, image=self.images["call"], bg="white", bd=0)
        call_btn.pack(side=tk.LEFT, padx=10)
        
        video_btn = tk.Button(header_actions, image=self.images["video"], bg="white", bd=0)
        video_btn.pack(side=tk.LEFT, padx=10)
        
        menu_btn = tk.Button(header_actions, image=self.images["menu"], bg="white", bd=0)
        menu_btn.pack(side=tk.LEFT, padx=10)
        
        # Chat messages area
        chat_body = tk.Frame(self.chat_frame, bg="#f5f7fb")
        chat_body.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.chat_canvas = tk.Canvas(chat_body, bg="#f5f7fb", bd=0, highlightthickness=0)
        chat_scrollbar = tk.Scrollbar(chat_body, orient=tk.VERTICAL, command=self.chat_canvas.yview)
        
        self.chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for messages
        self.messages_frame = tk.Frame(self.chat_canvas, bg="#f5f7fb")
        self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw", width=self.chat_canvas.winfo_reqwidth())
        
        # Update canvas scroll region when frame size changes
        self.messages_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(
            scrollregion=self.chat_canvas.bbox("all")))
        
        # Message input area
        message_input_frame = tk.Frame(self.chat_frame, bg="white", height=70)
        message_input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        message_input_frame.pack_propagate(False)
        
        # Attachments and input
        attachments_frame = tk.Frame(message_input_frame, bg="white")
        attachments_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Attachment buttons
        attach_btn = tk.Button(attachments_frame, image=self.images["attach"], bg="white", bd=0,  command=self.send_file_request)
        attach_btn.pack(side=tk.LEFT, padx=5)
        
        image_btn = tk.Button(attachments_frame, image=self.images["image"], bg="white", bd=0)
        image_btn.pack(side=tk.LEFT, padx=5)
        self.file_button.pack(side=tk.RIGHT, padx=5)
        # Message entry
        self.message_entry = tk.Entry(attachments_frame, font=("Segoe UI", 10), bd=0, bg="#f5f5f5")
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=8)
        self.message_entry.insert(0, "Type your message here")
        send_btn = tk.Button(attachments_frame, image=self.images["send"], bg="white", bd=0, 
                            command=self.send_message)
        send_btn.pack(side=tk.LEFT, padx=5)
    
    def add_conversation(self, name, last_message, time_ago, is_starred=False, is_selected=False):
        # Create a frame for the conversation
        bg_color = "#e6f2ff" if is_selected else "white"
        frame = tk.Frame(self.convo_list_frame, bg=bg_color, bd=0, height=80)
        frame.pack(fill=tk.X, padx=5, pady=2)
        frame.pack_propagate(False)
        
        # Left side with profile picture
        profile_label = tk.Label(frame, image=self.images["profile"], bg=bg_color)
        profile_label.pack(side=tk.LEFT, padx=10)
        
        # Right side with conversation info
        info_frame = tk.Frame(frame, bg=bg_color)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Top row with name and time
        top_row = tk.Frame(info_frame, bg=bg_color)
        top_row.pack(fill=tk.X, expand=True)
        
        name_label = tk.Label(top_row, text=name, font=("Segoe UI", 10, "bold"), anchor="w", bg=bg_color)
        name_label.pack(side=tk.LEFT)
        
        time_label = tk.Label(top_row, text=time_ago, font=("Segoe UI", 8), fg="#9e9e9e", bg=bg_color)
        time_label.pack(side=tk.RIGHT)
        
        # Message preview
        message_label = tk.Label(info_frame, text=last_message, font=("Segoe UI", 9), 
                                fg="#757575", anchor="w", justify=tk.LEFT, bg=bg_color)
        message_label.pack(fill=tk.X, pady=(5, 0), anchor="w")
        
        # Star icon
        star_img = self.images["star"] if is_starred else self.images["star_empty"]
        star_btn = tk.Button(frame, image=star_img, bg=bg_color, bd=0)
        star_btn.pack(side=tk.RIGHT, padx=10, anchor="n", pady=10)
        
        # Selection indicator if selected
        if is_selected:
            indicator = tk.Frame(frame, width=4, bg="#2979ff")
            indicator.place(x=0, y=0, relheight=1.0)
        
        # Store the frame in a list so we can access it later
        if not hasattr(self, 'conversation_frames'):
            self.conversation_frames = []
        
        self.conversation_frames.append((frame, name))
        
        # Bind click event to select conversation
        frame.bind("<Button-1>", lambda e, n=name: self.select_conversation(n))
    
    def add_message(self, sender_name, message_text, timestamp, is_sender=False):
        # Create message container
        align = tk.RIGHT if is_sender else tk.LEFT
        justify = tk.RIGHT if is_sender else tk.LEFT
        bg_color = "#dcf8c6" if is_sender else "white"
        
        message_container = tk.Frame(self.messages_frame, bg="#f5f7fb")
        message_container.pack(fill=tk.X, padx=10, pady=5, anchor='e' if is_sender else 'w')
        
        # Add profile picture for recipient messages
        if not is_sender:
            profile_label = tk.Label(message_container, image=self.images["profile"], bg="#f5f7fb")
            profile_label.pack(side=tk.LEFT, padx=(0, 10), anchor='n')
        
        # Message bubble
        bubble_frame = tk.Frame(message_container, bg=bg_color, bd=0, padx=10, pady=10)
        bubble_frame.pack(side=align)
        
        if is_sender:
            sender_label = tk.Label(bubble_frame, text="You", font=("Segoe UI", 9, "bold"), 
                                   bg=bg_color, anchor="e")
        else:
            sender_label = tk.Label(bubble_frame, text=sender_name, font=("Segoe UI", 9, "bold"), 
                                   bg=bg_color, anchor="w")
        sender_label.pack(anchor="w" if not is_sender else "e")
        
        message_label = tk.Label(bubble_frame, text=message_text, font=("Segoe UI", 10), 
                               bg=bg_color, anchor="w", justify=tk.LEFT, wraplength=400)
        message_label.pack(pady=(5, 5), anchor="w" if not is_sender else "e")
        
        time_label = tk.Label(bubble_frame, text=timestamp, font=("Segoe UI", 8), 
                             fg="#757575", bg=bg_color)
        time_label.pack(anchor="e" if is_sender else "w")
        
        # Scroll to bottom of chat
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def select_conversation(self, name):
        # Clear current messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        # Update header
        self.header_name.config(text=name)
        
        # Update conversation list selection
        for frame, frame_name in self.conversation_frames:
            frame.config(bg="white")
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for sub_widget in widget.winfo_children():
                        sub_widget.config(bg="white")
                else:
                    widget.config(bg="white")
            
            # Remove any existing selection indicators
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame) and child.winfo_width() == 4:
                    child.destroy()
        
        # Select the clicked conversation
        for frame, frame_name in self.conversation_frames:
            if frame_name == name:
                frame.config(bg="#e6f2ff")
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        widget.config(bg="#e6f2ff")
                        for sub_widget in widget.winfo_children():
                            sub_widget.config(bg="#e6f2ff")
                    else:
                        widget.config(bg="#e6f2ff")
                
                # Add selection indicator
                indicator = tk.Frame(frame, width=4, bg="#2979ff")
                indicator.place(x=0, y=0, relheight=1.0)
        

    def send_message(self):
        message = self.message_entry.get()
        if message and message != "Type your message here":
            now = datetime.datetime.now()
            timestamp = now.strftime("%I:%M %p").lower()
            
            self.add_message("You", message, timestamp, True)
            self.message_entry.delete(0, tk.END)
            
            # Simulate a response after a short delay
            self.root.after(2000, self.simulate_response)
    
    def simulate_response(self):
        responses = [
            "I see, that's interesting!",
            "Thanks for the information.",
            "I'll get back to you on that soon.",
            "Great! Let's discuss more details.",
            "I understand. What's the next step?",
            "Perfect! I'll prepare everything."
        ]
        
        response = random.choice(responses)
        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M %p").lower()
        
        selected_convo = self.header_name.cget("text")
        self.add_message(selected_convo, response, timestamp, False)
    
    def setup_bindings(self):
        # Clear default text when clicking on entry fields
        def clear_default_text(event):
            if event.widget.get() == "Search":
                event.widget.delete(0, tk.END)
            elif event.widget.get() == "Type your message here":
                event.widget.delete(0, tk.END)
        
        # Restore default text when focus is lost and field is empty
        def restore_default_text(event):
            if event.widget.get() == "" and event.widget == self.message_entry:
                event.widget.insert(0, "Type your message here")
        
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.bind("<FocusIn>", clear_default_text)
                widget.bind("<FocusOut>", restore_default_text)
        
        self.message_entry.bind("<FocusIn>", clear_default_text)
        self.message_entry.bind("<FocusOut>", restore_default_text)
        
        # Send message when Enter is pressed
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Make the chat area responsive to window size changes
        self.root.bind("<Configure>", self.on_window_resize)
    
    def on_window_resize(self, event):
        # Update message wrapping based on window size
        if hasattr(self, 'messages_frame'):
            for widget in self.messages_frame.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        for label in child.winfo_children():
                            if isinstance(label, tk.Label) and not label.cget("text") in ["You", "10:17 am", "10:29 am", "10:33 am"]:
                                # Calculate a good wraplength based on window size
                                wraplength = min(400, max(200, int(self.root.winfo_width() * 0.4)))
                                label.config(wraplength=wraplength)
        
        # Update canvas width for messages
        if hasattr(self, 'chat_canvas'):
            self.chat_canvas.itemconfig(1, width=self.chat_canvas.winfo_width())

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatApp(root)
    root.mainloop()