import gradio as gr
import smbus
from time import sleep

i2c = smbus.SMBus(1)
ADC_ADDR = 0x48 

command_for_channel_5 = 0x45 #Y
command_for_channel_6 = 0x46 #X

pot_values = [127, 127]
pot_labels = ["X axis", "Y axis"]

def update_bars():
    global pot_values
    
    i2c.write_byte(ADC_ADDR, command_for_channel_6)
    i2c.read_byte(ADC_ADDR) 
    val_x = i2c.read_byte(ADC_ADDR)
    
    i2c.write_byte(ADC_ADDR, command_for_channel_5)
    i2c.read_byte(ADC_ADDR) 
    val_y = i2c.read_byte(ADC_ADDR)
    
    pot_values = [val_x, val_y]

    result = ""
    bar_length = 20
    for i, value in enumerate(pot_values):
        filled = int((value / 255) * bar_length)
        bar = "+" * filled + "-" * (bar_length - filled)
        percent = int((value / 255) * 100)
        result += f"**{pot_labels[i]}:** [{bar}] {percent}%\n\n"
    
    return result

with gr.Blocks() as demo:
    gr.Markdown("Magic")
    gr.Markdown("Move joystick.")
    text_display = gr.Markdown()
    
    timer = gr.Timer(value=0.1)
    timer.tick(fn=update_bars, outputs=text_display)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")