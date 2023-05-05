import board
import touchio

for name in dir(board):
    if name.startswith('_'):
        continue
    pin = getattr(board, name)
    try:
        a = touchio.TouchIn(pin)
        a.deinit()
        print(pin, "can be used for touch")
    except Exception as e: 
        print(pin, "cannot be used for touch")
        print(e)

