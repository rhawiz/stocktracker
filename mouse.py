# from time import sleep
#
# import uinput
#
# events = (
#     uinput.REL_X,
#     uinput.REL_Y,
#     uinput.BTN_LEFT,
#     uinput.BTN_RIGHT,
# )
#
# with uinput.Device(events) as device:
#     for x in range(0, 1920):
#         # syn=False to emit an "atomic" (5, 5) event.
#         device.emit(uinput.REL_X, x, syn=False)
#
#         # Just for demonstration purposes: shows the motion. In real
#         # application, this is of course unnecessary.
#         sleep(0.1)
from time import sleep

import uinput

#
# def main():
#     events = (
#         uinput.REL_X,
#         uinput.REL_Y,
#         uinput.BTN_LEFT,
#         uinput.BTN_RIGHT,
#     )
#
#     with uinput.Device(events) as device:
#         while True:
#             # syn=False to emit an "atomic" (5, 5) event.
#             device.emit(uinput.REL_X, 1, syn=True)
#
#             # Just for demonstration purposes: shows the motion. In real
#             # application, this is of course unnecessary.
#             sleep(0.25)
from pymouse import PyMouse


def main():
    m = PyMouse()
    for i in range(0, 5):
        print(i)
        sleep(1)
    while True:
        for x in range(250, 1571):
            m.move(x, 500)
            sleep(0.3)

        m.move(1571, 500)
        m.release(1571, 500)
    # for x in range(300, 1200):
    #     m.move(x, 500)
    #
    #     sleep(0.25)


if __name__ == "__main__":
    main()
