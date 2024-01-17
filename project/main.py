from Game import Game
import sys
sys.setrecursionlimit(1000000000)

with open("temp.txt", "w") as file:
    file.write("")

g = Game()
g.play()



# for i in Game.distance:
#     print(round(i,5))

# from Board import Board

# b=Board()
# print(b.get_distance(8,42))
