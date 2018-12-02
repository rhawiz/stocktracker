from time import sleep





def mouse(start_x, end_x):
    m = PyMouse()
    for i in range(0, 2):
        print(i)
        sleep(1)
    c = 0
    while True:
        c += 1
        for x in range(start_x, end_x, 2):
            m.move(x, 500)
            sleep(0.001)

        # m.press(start_x, 500)
        m.move(start_x, 500)
        m.drag(end_x, 500)
        if c == 2:
            break





#
if __name__ == "__main__":
    mover(1800)
