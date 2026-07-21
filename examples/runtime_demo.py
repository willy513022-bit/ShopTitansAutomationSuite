
from runtime.capture import Capture
from runtime.click import ClickExecutor
img=Capture().grab()
print("Runtime Demo")
print("capture =",img.shape)
print(ClickExecutor().click(640,360))
