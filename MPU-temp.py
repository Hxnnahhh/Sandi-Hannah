import gradio as gr
from smbus import SMBus
import time
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
i2c = SMBus(1)
MPU_ADDR = 0x68

CONF_PWR = 0x6B
CONF_ACC = 0x1C
CONF_GYR = 0x1B

TEMP_OUT_H = 0x41
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43


def init_MPU():
    i2c.write_byte_data(MPU_ADDR, CONF_PWR, 0x01)
    i2c.write_byte_data(MPU_ADDR, CONF_ACC, 0x00) 
    i2c.write_byte_data(MPU_ADDR, CONF_GYR, 0x00) 
    time.sleep(0.1)


def combine_bytes(msb, lsb):
    value = (msb << 8) | lsb
    if value & 0x8000:
        value -= 65536
    return value


def get_all_data():
    t_bytes = i2c.read_i2c_block_data(MPU_ADDR, TEMP_OUT_H, 2)
    temp = combine_bytes(t_bytes[0], t_bytes[1]) / 340.0 + 36.53
    a_data = i2c.read_i2c_block_data(MPU_ADDR, ACCEL_XOUT_H, 6)
    ax = combine_bytes(a_data[0], a_data[1]) / 16384.0
    ay = combine_bytes(a_data[2], a_data[3]) / 16384.0
    az = combine_bytes(a_data[4], a_data[5]) / 16384.0
    g_data = i2c.read_i2c_block_data(MPU_ADDR, GYRO_XOUT_H, 6)
    gx = combine_bytes(g_data[0], g_data[1]) / 131.0
    gy = combine_bytes(g_data[2], g_data[3]) / 131.0
    gz = combine_bytes(g_data[4], g_data[5]) / 131.0
    result = f"temperature: {temp:.2f} °C\n\n"
    result += f"Speed(g):\nX: {ax:.2f} | Y: {ay:.2f} | Z: {az:.2f}\n\n"
    result += f"Gyroscope (°/s):\n X: {gx:.2f} | Y: {gy:.2f} | Z: {gz:.2f}"
    return result



init_MPU() 

with gr.Blocks() as demo:
    gr.Markdown("# MPU-6050:Assighment")
    display = gr.Markdown("Downloading resources...")
    timer = gr.Timer(value=0.5)
    timer.tick(fn=get_all_data, outputs=display)    
try:
    demo.launch(server_name="0.0.0.0")
except KeyboardInterrupt:
    GPIO.cleanup()