import gradio as gr 
from RPi import GPIO
from basic_buzzer import BuzzerService

def play_tone(pin,  freq, dur, duty):
    buzzer =BuzzerService(int(pin))
    buzzer.play_tone(float(freq), float(dur), float(duty))
    buzzer.stop()


with gr.Blocks(title="GPIO Lab 1") as demo:
    gr.Markdown("## Buzzer Control")
    with gr.Row():
        buzzer_pin = gr.Number(label = "Buzzer")
        frequency = gr.Number(label = "Frequency")
        duration = gr.Number(label = "Duration")
        duty_cycle = gr.Number(label = "Duty Cycle")
        play_button = gr.Button("Play tone")

    play_button.click(play_tone, inputs = [buzzer_pin, frequency, duration, duty_cycle])





demo.launch(
    server_name = "0.0.0.0",
    server_port =  7861,
)
