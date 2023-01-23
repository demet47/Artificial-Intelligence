import copy
from collections import deque
from sre_constants import FAILURE
import queue
import requests

search_list=["BFS","DFS","UCS","GS","A*","A*2"]
search="BFS"
target_url="https://www.cmpe.boun.edu.tr/~emre/courses/cmpe480/hw1/input1.txt"

txt = requests.get(target_url).text

linesSplit = txt.splitlines()
input_grid = [[i for i in l] for l in linesSplit]


def TIE_BREAKER(me, other):
    priority_map = {"left" : 1, "down" : 2, "right" : 3, "up" : 4}
    index_of_char_me = me.history.rfind(",") + 2
    index_of_char_other = other.history.rfind(",") + 2
    if index_of_char_me == 1:
        index_of_char_me = 0
    if index_of_char_other == 1:
        index_of_char_other = 0
    char_me = me.history[index_of_char_me]
    char_other = other.history[index_of_char_other]
    if char_me == char_other:
        return priority_map.get(me.history[index_of_char_me + 2:]) < priority_map.get(other.history[index_of_char_other + 2:])
    return char_me < char_other

class Board:
    def __init__(self, init_grid, index, cost, history, problem_code):
        self.grid = init_grid
        self.index = index
        self.cost = cost
        self.history = history
        self.heuristic = self.heuristic_calculate(problem_code)
        self.problem_code = problem_code

    
    def __lt__(self, other):
        if (self.problem_code == "BFS") | (self.problem_code == "DFS") | (self.problem_code == "UCS"):
            if (self.problem_code == "UCS") & (self.cost == other.cost):
                return TIE_BREAKER(self, other)
            return self.cost < other.cost
        if self.heuristic == other.heuristic:
            return TIE_BREAKER(self, other)
        return self.heuristic < other.heuristic
    
    def __eq__(self, other):
        if ((self.grid == other.grid) & (self.cost == other.cost)):
            if (self.problem_code == "A*") | (self.problem_code == "GS"):
                if(self.heuristic == other.heuristic):
                    return True
                return False
            return True
        return False

    def __hash__(self):
        if (self.problem_code == "A*") | (self.problem_code == "GS"):
            return hash((self.cost, tuple([tuple(i) for i in self.grid]), self.heuristic))
        return hash((self.cost,tuple([tuple(i) for i in self.grid])))

    def heuristic_calculate(self, problem_code):
        if (problem_code == "GS") | (problem_code == "A*"): ##!!
            row_count = 0
            col_count = 0
            pegged_row = [False] * len(self.grid)
            pegged_col = [False] * len(self.grid[0])
            for r in range(len(self.grid)):
                for c in range(len(self.grid[0])):
                    if self.grid[r][c] != ".":
                        pegged_row[r] = True
                        pegged_col[c] = True
            
            for i in pegged_row:
                if i == True:
                    row_count += 1
            for i in pegged_col:
                if i == True:
                    col_count += 1
            if problem_code == "GS":
                return min(row_count, col_count)
            else:
                return min(row_count, col_count) + self.cost

class BoardGrid:
    def __init__(self, character, row, column):
        self.row = row
        self.column = column
        self.character = character

def get_char(board_grid):
    return board_grid.character

def jump(row,column,direction, in_grid):
    success = False
    copy_grid = copy.deepcopy(in_grid)
    horizontal = 0
    vertical = 0
    return_score = 0

    if direction == "r":
        return_score = 2
        horizontal = 1
    elif direction == "l":
        return_score = 4
        horizontal = -1
    elif direction == "u":
        return_score = 1
        vertical = - 1
    else: #if direction == "d"
        return_score = 3
        vertical = 1    


    if horizontal != 0:
        count_steps = 1
        edge = len(in_grid[0])
        while ((column + count_steps * horizontal) != -1) & ((column + count_steps * horizontal) != edge):
            if copy_grid[row][column + count_steps * horizontal] == ".":
                copy_grid[row][column + count_steps * horizontal] = in_grid[row][column]
                copy_grid[row][column] = "."
                success = True
                break
            else:
                copy_grid[row][column + count_steps * horizontal] = "."
                count_steps += 1

    elif vertical != 0:
        count_steps = 1
        edge = len(in_grid)
        while ((row + count_steps * vertical) != -1) & ((row + count_steps * vertical) != edge):
            if copy_grid[row + count_steps * vertical][column] == ".":
                copy_grid[row + count_steps * vertical][column] = in_grid[row][column]
                copy_grid[row][column] = "."
                success = True
                break
            else:
                
                copy_grid[row + count_steps * vertical][column] = "."
                count_steps += 1
    
    if success:
        return copy_grid, return_score, success  
    else:
        return in_grid, return_score, success

def EMPTY(fringe, problemCode):
    if (problemCode == "UCS") | (problemCode == "BFS") | (problemCode == "GS") | (problemCode == "A*"):
        return fringe.empty()
    elif problemCode == "DFS":
        return len(fringe) == 0
    
def ADD_TO_FRINGE(fringe, new_board, problem_code):
    if (problem_code == "UCS") | (problem_code == "BFS") | (problem_code == "GS") | (problem_code == "A*"):
        fringe.put(new_board)
    if problem_code == "DFS":
        fringe.append(new_board)
       
def NODE_REMOVE(fringe, problemCode):
    if (problemCode == "UCS") | (problemCode == "GS") | (problemCode == "A*"):
        return fringe.get()
    elif problemCode == "DFS":
        return fringe.pop()
    elif problemCode == "BFS":
        return fringe.get()

def GOAL_TEST(node):
    count = 0
    for row in node.grid:
        for element in row:
            if element != ".":
                count += 1
                if count > 1:
                    return False
    if count == 1:
        return True
    else: 
        return False

def INSERT_ALL(fringe, node, problemCode):
    grid_height = len(node.grid)
    grid_width = len(node.grid[0])
    current_grid = node.grid
    queue = []

    for r in range(grid_height):
        for c in range(grid_width):
            if current_grid[r][c] == ".":
                continue
            else:
                queue.append(BoardGrid(current_grid[r][c], r, c))
   
    queue.sort(key = get_char)

    if (problemCode == "BFS") | (problemCode == "DFS"):
        for current in queue:
            r = current.row
            c = current.column
            if c != 0: #if not left alligned
                if current_grid[r][c-1] != ".":
                    [return_grid, return_score, success] = jump(r,c, "l", current_grid)
                    if success:
                        new_history = node.history + (", " if node.history != "" else "") + current_grid[r][c] + " left"
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score, new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            if r != grid_height - 1: #if not bottom alligned
                if current_grid[r+1][c] != ".":
                    [return_grid, return_score, success] = jump(r,c, "d", current_grid)
                    if success:
                        new_history = node.history +  (", " if node.history != "" else "") + current_grid[r][c] + " down"
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score,new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            if c != grid_width - 1: #if not right oriented
                if current_grid[r][c+1] != ".":
                    [return_grid, return_score, success] = jump(r,c, "r", current_grid)
                    if success:                
                        new_history = node.history + (", " if node.history != "" else "") + current_grid[r][c] + " right"                
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score,new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            if r != 0: #if not top alligned
                if current_grid[r-1][c] != ".":
                    [return_grid, return_score, success] = jump(r,c, "u", current_grid)
                    if success:
                        new_history = node.history + (", " if node.history != "" else "") + current_grid[r][c] + " up"
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score,new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
    else:
        for current in queue:
            r = current.row
            c = current.column
            if r != 0: #if not top alligned
                if current_grid[r-1][c] != ".":
                    [return_grid, return_score, success] = jump(r,c, "u", current_grid)
                    if success:
                        new_history = node.history + (", " if node.history != "" else "") + current_grid[r][c] + " up"
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score,new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            if c != grid_width - 1: #if not right oriented
                if current_grid[r][c+1] != ".":
                    [return_grid, return_score, success] = jump(r,c, "r", current_grid)
                    if success:                
                        new_history = node.history + (", " if node.history != "" else "") + current_grid[r][c] + " right"                
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score,new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            if r != grid_height - 1: #if not bottom alligned
                if current_grid[r+1][c] != ".":
                    [return_grid, return_score, success] = jump(r,c, "d", current_grid)
                    if success:
                        new_history = node.history +  (", " if node.history != "" else "") + current_grid[r][c] + " down"
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score,new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            if c != 0: #if not left alligned
                if current_grid[r][c-1] != ".":
                    [return_grid, return_score, success] = jump(r,c, "l", current_grid)
                    if success:
                        new_history = node.history + (", " if node.history != "" else "") + current_grid[r][c] + " left"
                        new_board = Board(return_grid,node.index + 1 ,node.cost + return_score, new_history, problemCode)
                        ADD_TO_FRINGE(fringe, new_board, problemCode)
            

#the initial node will come here with the initial state pushed already
def TREE_SEARCH(problemCode, fringe):
    count_removed = 0
    while(1):
        if EMPTY(fringe, problemCode) == True:
            return FAILURE, count_removed
        node = NODE_REMOVE(fringe, problemCode)
        count_removed += 1
        if GOAL_TEST(node):
            return node, count_removed
        INSERT_ALL(fringe, node, problemCode)

#the initial node will come here with the initial state pushed already
def GRAPH_SEARCH(problem_code, fringe):
    closed = set()
    count_removed = 0
    while(1):
        if EMPTY(fringe, problem_code) == True:
            return FAILURE, count_removed
        node = NODE_REMOVE(fringe, problem_code)
        count_removed += 1
        if GOAL_TEST(node):
            return node, count_removed
        if closed.__contains__(node) == False:
            closed.add(node)
            INSERT_ALL(fringe, node, problem_code)

    return count_removed
            
def main():
    s = input_grid
    
    fifo_queue = queue.Queue()
    fifo_queue.put(Board(s, 0,0, "", "BFS"))
    [r, removed_node_num] = TREE_SEARCH("BFS", fifo_queue)
    print("BFS")
    print("Number of removed nodes: ", removed_node_num)
    print("Path cost: ", r.cost)
    r.history += ","
    print("Solution: ", r.history)
    print()


    stack = [Board(s, 0, 0, "", "DFS")]
    [r, removed_node_num]= TREE_SEARCH("DFS", stack)
    print("DFS")
    print("Number of removed nodes: ", removed_node_num)
    print("Path cost: ", r.cost)
    r.history += ","
    print("Solution: ", r.history)
    print()


    q = queue.PriorityQueue()
    q.put(Board(s, 0, 0, "", "UCS"))
    [r, removed_node_num] = TREE_SEARCH("UCS", q)
    print("UCS")
    print("Number of removed nodes: ", removed_node_num)
    print("Path cost: ", r.cost)
    r.history += ","
    print("Solution: ", r.history)
    print()


    gs = queue.PriorityQueue()
    gs.put(Board(s, 0, 0, "", "GS"))
    [r, removed_node_num] = GRAPH_SEARCH("GS", gs)
    print("GS")
    print("Number of removed nodes: ", removed_node_num)
    print("Path cost: ", r.cost)
    r.history += ","
    print("Solution: ", r.history)
    print()
    

    astr = queue.PriorityQueue()
    astr.put(Board(s, 0, 0, "", "A*"))
    [r, removed_node_num] = GRAPH_SEARCH("A*", astr)
    print("A*")
    print("Number of removed nodes: ", removed_node_num)
    print("Path cost: ", r.cost)
    r.history += ","
    print("Solution: ", r.history)
    print()

    

if __name__ == '__main__':
    main()



#A* ve UCS sorunlu. version2.py en doğru çalışan versiyon