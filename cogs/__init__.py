import os

def get_cog_names():
    cog_list = []
    
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith(".py") and file != "__init__.py":
            cog_list.append(f"cogs.{file[:-3]}")
    
    return cog_list