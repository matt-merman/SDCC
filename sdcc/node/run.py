from src.main import * 
import sys

def run():
    
    id = int(sys.argv[1])
    port = int(sys.argv[2])
    type = int(sys.argv[3])
    node = Node(id, port, type)
    node.initialize()

if __name__ == '__main__':
    run()
