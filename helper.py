import os
import yaml # pyyaml
from pathlib import Path
import sys
import typer

app = typer.Typer()

# A node corresponds to a folder or a file
class Node():
    def __init__(self, name):
        self.name = name
        self.ismdfile = None
        self.childs = []
        self.order = None
        self.visible = True

@app.callback(invoke_without_command=True)
def update():
    print("Haha callback works")

@app.command()
def reorder(node_name: str):
    print(node_name)

if __name__ == '__main__':
    app()




