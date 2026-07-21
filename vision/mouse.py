import time
import pyautogui
pyautogui.FAILSAFE=True

def move_mouse(x,y,duration=0.2): pyautogui.moveTo(x,y,duration=duration)
def drag_mouse(start_x,start_y,end_x,end_y,duration=0.8): pyautogui.moveTo(start_x,start_y,duration=0.2); pyautogui.dragTo(end_x,end_y,duration=duration,button="left")
def scroll_mouse(x,y,amount,pause=0.8): pyautogui.moveTo(x,y,duration=0.2); pyautogui.scroll(amount); time.sleep(pause)
