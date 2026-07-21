from datetime import datetime
def log(level:str,message:str)->None:print(f"{datetime.now().strftime('%H:%M:%S')} {level.upper():<5} {message}")
