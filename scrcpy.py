import customtkinter
import tkinter
from PIL import Image ,ImageTk,ImageDraw
import os
import subprocess
from tkinter import filedialog


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root=customtkinter.CTk()
root.title("SCRCPY")
root.geometry("750x500")
root.resizable(False,False)


wallpaper=customtkinter.CTkImage(dark_image=Image.open("wallpaper.jpg"),size=(750,500))

set_wallpaper=customtkinter.CTkLabel(root,image=wallpaper)
set_wallpaper.place(x=0,y=0,relheight=1,relwidth=1)

img1=customtkinter.CTkImage(dark_image=Image.open("codingframe.jpeg"),size=(60,60))
img2=customtkinter.CTkImage(dark_image=Image.open("iconcross.png"),size=(18,18))
img3=customtkinter.CTkImage(dark_image=Image.open("Border_with.png"),size=(526,350))

global text_side
text_side=800/2+350


def sidein():
    global text_side
    text_side-=30
    if text_side>=80:
        ip_box.place(x=text_side,y=540/2,anchor="center")   #ip_barin.configure(text=text_side)   ,isse Coordinates malum pdte hai
        root.after(10,sidein)

def sideout():
    global text_side
    text_side+=30
    if text_side<=750:
        ip_box.place(x=text_side,y=540/2,anchor="center")
        root.after(10,sideout)
     
def login():
    pass

def get_scrcpy_executable():
  
    script_dir = os.path.dirname(__file__)  # Directory of the script
    scrcpy_folder = os.path.join(script_dir, 'scrcpy')  # Path to the scrcpy folder

    if os.name == 'nt':  
        return os.path.join(scrcpy_folder, 'scrcpy.exe')
    else:  
        return os.path.join(scrcpy_folder, 'scrcpy')

def start_mirror_wired():
    
    command = [get_scrcpy_executable()]

    orientation = orientation_var.get()
    if orientation != 'None':
        command.extend(['--lock-screen-orientation', orientation])
    
    bitrate = bitrate_var.get()
    if bitrate and bitrate != 'None':
        command.extend(['-b', bitrate])
    
    if record_var.get():
        file_path = os.path.join(recording_folder_var.get(), 'recording.mp4')
        command.extend(['--record', file_path])

    print("Running command:", ''.join(command))
    subprocess.Popen(command, cwd=os.path.join(os.path.dirname(__file__), 'scrcpy'))

def wireless_rec():
    pass



def select_recording_folder():
    folder = filedialog.askdirectory()
    if folder:
        recording_folder_var.set(folder)
 
def create_circular_image(image_path, output_size=(100, 100)):
    img = Image.open(image_path).convert("RGBA")
    img = img.resize(output_size)
    
    mask = Image.new('L', output_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, output_size[0], output_size[1]),255)

    img.putalpha(mask)
    return img


circular_image = create_circular_image("sneak.png")       
photo = ImageTk.PhotoImage(circular_image)      
      
label = customtkinter.CTkLabel(root,text='', fg_color='transparent',image=photo)
label.image = photo  
label.place(x=10, y=0)






frame=customtkinter.CTkLabel(root,image=img3,text="")
frame.place(x=112,y=77)



#Wired wla kaam hai
#Select bitrate
wired=customtkinter.CTkLabel(frame, text="Wired Screen Method",font=("Imprint MT Shadow",20),fg_color="#262626")
wired.place(x=12,y=10)

bit_bold=customtkinter.CTkFont(frame,weight="bold",size=12)
entry1=customtkinter.CTkLabel(frame, text="Enter the Bitrate",text_color="#66ffff",font=bit_bold,fg_color="#262626")
entry1.place(x=12,y=50)

bitrate_options = ["Default", "2M", "4M", "6M", "10M"]
bitrate_var = customtkinter.StringVar(value='None')

bitrate_menu = customtkinter.CTkOptionMenu(frame, values=bitrate_options, variable=bitrate_var,fg_color="#262626")
bitrate_menu.place(x=110,y=52)



#select Orientation
bold_font=customtkinter.CTkFont(frame,weight="bold")
entry2=customtkinter.CTkLabel(frame, text="Enter the Orientation",font=bold_font,text_color="#66ffff",fg_color="#262626")
entry2.place( x=12,y=95)

orientation_options = ["None", "Portrait", "Landscape"]
orientation_var = customtkinter.StringVar(value='None')

orientation_menu = customtkinter.CTkOptionMenu(frame, values=orientation_options , variable=orientation_var,fg_color="#262626")
orientation_menu.place(x=150,y=95)

#start Wired
STARTW=customtkinter.CTkButton(frame,command=start_mirror_wired,cursor="hand2",text="START MIRROR",fg_color="green",hover_color="#00cc00",border_width=1,bg_color="#333333",border_color="#00cc00")
STARTW.place( x=15,y=135)


#record krne ka 
record_var = customtkinter.BooleanVar()
recording_folder_var = customtkinter.StringVar(value=os.path.dirname(__file__))

record_checkbox = customtkinter.CTkCheckBox(frame, text="Record Screen",text_color="#ff0000", bg_color="#262626",variable=record_var)
record_checkbox.place(x=160,y=136)

select_folder_button = customtkinter.CTkButton(frame, text="Select Recording Folder",fg_color="#66b3ff",border_color="#66b3ff",border_width=1,command=select_recording_folder)
select_folder_button.place(x=280,y=135)



root.mainloop()
