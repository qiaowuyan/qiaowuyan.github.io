import os
from pathlib import Path
import yaml
import sys

# join the path for path written to mkdocs.yml
# we can't set Windows style path to mkdocs so have to use hard-code path join
def pjoin(*path_list):
    return "/".join(path_list)

# get md files name under this position, position has to be a Path
def get_mdfiles(position):
    return [item.name for item in position.glob('*.md')]
    
# get directories under this position, postition has to be a Path
# ignore some names
dir_ignore = ["assets"]
def get_dirs(position):
    return [item.name for item in position.iterdir() if item.is_dir() and item.name not in dir_ignore]

# recursively list the file and generate mkdocs.yml
# you can set the order when order = 1
def dfs_find(cur_prefix, fa_list, cur_position, order, argv_list = None):

    print (f"\n\n[[ Get Into {cur_prefix} ]]")

    # get md files and directories names (without parent directory path)
    files = get_mdfiles(cur_position)
    dirs = get_dirs(cur_position)
    file_and_dir = files + dirs
    
    print ("files and directories: ", file_and_dir)
    
    # adjust / maintain the order
    order_path = cur_position / ".order"
    order_list = []
    try:
        with open(order_path, "r") as orderf:
            order_list = orderf.read().split('\n')
    except Exception as e:
        pass

    print("order_list is: ", order_list)
    
    # get files or dirs that are not in order list
    notin_list = list(filter(lambda t: t not in order_list, file_and_dir))
    notin_list = sorted(notin_list, key = lambda t: os.stat(cur_position / t).st_ctime)

    # update order list
    order_list = order_list + notin_list
    order_len = len(order_list)

    print("This is order list: ", order_list)

    # modify order
    if (order and ((cur_prefix in argv_list) or (len(argv_list) == 0))):
        while 1:
            os.system("cls")
            new_order_list = [i for i in range(0, order_len)]
            print("The current order of files in ", cur_position.name)
            for node, cnt in enumerate(order_list):
                print (node, cnt)
            command = input("Change the order:\n \
1. sw a b ---- swap ath and bth\n \
2. up a   ---- up ath\n \
3. dn a   ---- down ath\n \
4. input a whole new order (should be a permutation), say a, b, c, then ath file would be in the first place then\n \
5. e      ---- exit\n \
6. ea     ---- exit for all\n")
            commands = command.split()
            print(commands)
            if (commands[0] == "e"):
                print ("exit")
                break
            
            elif (commands[0] == "ea"):
                print ("exit")
                order = False
                break

            elif (commands[0] == "sw"):
                if (commands[1].isdigit() and commands[2].isdigit()):
                    a, b = int(commands[1]), int(commands[2])
                    if (a >= 0 and a < order_len and b >= 0 and b < order_len):
                        order_list[a], order_list[b] = order_list[b], order_list[a]
                    
            elif (commands[0] == "up"):
                if (commands[1].isdigit()):
                    a = int(commands[1])
                    if (a >= 1 and a < order_len):
                        order_list[a], order_list[a - 1] = order_list[a - 1], order_list[a]

            elif (commands[0] == "dn"):
                if (commands[1].isdigit()):
                    a = int(commands[1])
                    if (a >= 0 and a < order_len - 1):
                        order_list[a], order_list[a + 1] = order_list[a + 1], order_list[a]
            
            else:
                if (all(t.isdigit() for t in commands)):
                    num_list = [int(t) for t in commands]
                    counter = [t in num_list for t in range(0, order_len)]
                    if (len(num_list) == order_len and all(t == True for t in counter)):
                        for i, cnt in enumerate(num_list):
                            new_order_list[cnt] = order_list[num_list[i]]
                        order_list = new_order_list

    for node in order_list:
        node_path = cur_position / node

        # if this is a dir, dir dict is just {dir_name: dir_list}
        if (node_path.is_dir()):
            dir_list = []
            dfs_find(pjoin(cur_prefix, node), dir_list, node_path, order, argv_list)
            dir_dict = {node: dir_list}
            fa_list.append(dir_dict)

        # if this is a file
        # if index.md, {parent: node}
        # otherwise,   {node.stem: node}
        if (node_path.is_file()):
            file_dict = {node_path.stem if node != "index.md" else node_path.parent.name: pjoin(cur_prefix, node)}
            if (node == "index.md"):
                fa_list.insert(0, file_dict)
            else:
                fa_list.append(file_dict)

    # finally write updated order list back
    with open(cur_position / ".order", "w+") as order_path:
        order_path.write("\n".join(order_list))


# 打开yml文件，读取文件数据流
with open("mkdocs.yml","r", encoding="utf-8") as f:
    ayml=yaml.load(f.read(), Loader=yaml.Loader)

default = {'RABBIT': [{'ME': 'index.md'}]}
ayml["nav"] = [default]

argv_list = sys.argv[2:]

# current position is the Path of cwd
# current prefix is used to for json dict {test: posts/CPP/test.md}, here posts/CPP is cur prefix
cur_position = Path.cwd() / "docs" / "posts"
cur_prefix = "posts"
dfs_find(cur_prefix, ayml["nav"], cur_position, len(sys.argv) > 1 and sys.argv[1] == "order", argv_list)

print (ayml["nav"])

# output ayml to file
with open("mkdocs.yml","w", encoding="utf-8") as f:
    yaml.dump(ayml, f)
