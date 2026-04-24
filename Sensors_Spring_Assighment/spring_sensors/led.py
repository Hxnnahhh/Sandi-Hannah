def start_led(pwm_r, pwm_g, pwm_b):
    for pwm in [pwm_r, pwm_g, pwm_b]:
        pwm.start(0)


def set_color(pwm_r, pwm_g, pwm_b, x_val, y_val):
    r = (x_val / 255) * 100
    g = (y_val / 255) * 100
    b = (r + g) / 2
    pwm_r.ChangeDutyCycle(r)
    pwm_g.ChangeDutyCycle(g)
    pwm_b.ChangeDutyCycle(b)


def turn_off(pwm_r, pwm_g, pwm_b):
    set_color(pwm_r, pwm_g, pwm_b, 0, 0)
