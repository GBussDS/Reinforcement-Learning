import random

a= 0

class Game():
    def __init__(self, player1, player2):
        #Chose to treat the state as a 9 digit list, as concatenating the numbers in the matrix: [[0,0,0],[0,0,0],[0,0,0]] 
        self.state = [0,0,0,0,0,0,0,0,0]
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.player1
        self.win_count = [0,0,0]

        self.winner = None
        self.every_state = []
        
        self.every_state_setter()

    def train(self, train_times):
        self.player1.set_values(self)
        self.player2.set_values(self)

        for i in range(train_times):
            print(f"Current run: {i}", end ='\r')
            result = self.match()
            self.win_count[result - 1] += 1

            #Updates values and resets players historics
            self.player1.update_values()
            self.player2.update_values()
            self.player1.reset_historic()
            self.player2.reset_historic()
            self.state = [0,0,0,0,0,0,0,0,0]
        
        #Shows last match and results
        result = self.match(debug=True)
        self.win_count[result - 1] += 1
        print("Ganhador da final: " + str(result))
        print("Placar: " + str(self.win_count))


    def match(self, debug = False):
        self.current_player = random.choice([self.player1,self.player2]) #Chooses a random player to start

        winner = 0
        while winner == 0:
            new_state = self.current_player.play(self.state)
            self.state = new_state

            if debug == True:
                self.print_state()

            self.change_players()

            winner = check_winner(self.state)
            #Draw
            if winner == 3:
                return 3
            #Player 1 wins
            elif winner == 1:
                self.winner = self.player1
                return 1
            #Player 2 wins
            elif winner == 2:
                self.winner = self.player2
                return 2

    def change_players(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1
    
    def print_state(self):
        state = self.state.copy()
        for i in range(len(state)):
            if state[i] == 1:
                state[i] = "X"
            elif state[i] == 2:
                state[i] = "O"
            else:
                state[i] = " "

        for i in range(3):
            print(" " + state[0 + 3 * i] + " | " + state[1 + 3 * i] + " | " + state[2 + 3 * i] + " ")
            if i != 2:
                print("-----------")
        
        print("###########")
    
    def every_state_setter(self):
        state_number = 0

        #Appending the empty state
        current_state = [0,0,0,0,0,0,0,0,0]
        self.every_state.append(current_state.copy())

        current_index = 0

        # 3^9 is all the possible states in existance, since there is 9 digits with 3 options each
        while state_number < 3 ** 9 - 1:
            #Turns the 2 in 0 as since they have already reached the limit
            while current_state[current_index] == 2:
                current_state[current_index] = 0
                current_index += 1

            current_state[current_index] += 1
            current_index = 0
            
            self.every_state.append(current_state.copy())
            state_number += 1

class Player():
    def __init__(self, number, step_size, epsolon):
        #1 or 2
        self.play_number = number
        self.step_size = step_size
        self.epsolon = epsolon
        self.values = {}
        self.historic = {}
    
    def append_state(self, state_number, best_choice):
        #True when the choice was the best available
        self.historic[state_number] = best_choice

    def reset_historic(self):
        self.historic = {}

    def update_values(self):
        keys = list(self.historic.keys())

        #Updates the values backwards
        for i in range(len(keys)-2, -1, -1):
            if self.historic[keys[i]]:
                self.values[keys[i]] += self.step_size * (self.values[keys[i+1]] - self.values[keys[i]])
                print(str(keys[i]) + " " + str(self.values[keys[i]]))
                a = keys[i]
    
    def play(self, state):
        #checks the position of empty spaces
        zeros = []
        for i in range(len(state)):
            if state[i] == 0:
                zeros.append(i)
        
        options = []
        for index in zeros:
            option_state = state.copy()
            option_state[index] = self.play_number
            option_state_number = self._list_to_number(option_state)
            options.append(option_state_number)
        
        #Finds best option
        best_option = options[0]
        for option in options: 
            if self.values[option] > self.values[best_option]:
                best_option = option
        
        if len(options) != 1 and self.values[best_option] != 1:
            #Exploratory move
            chance = random.random()
            if chance <= self.epsolon or self.values[best_option] == 0:
                options.remove(best_option)
                best_option = options[random.randint(0,len(options)-1)]
                
                self.append_state(best_option, False)
                return self._number_to_list(best_option)

        #Best move
        self.append_state(best_option, True)
        return self._number_to_list(best_option)

    def set_values(self, game:Game):
        for state in game.every_state:
            state_number = self._list_to_number(state)
            winner = check_winner(state)
            if winner == 0:
                self.values[state_number] = 0.5
            elif winner == self.play_number or winner == 3:
                self.values[state_number] = 1
            else:
                self.values[state_number] = 0

    def _list_to_number(self, state_list):
        state_number = ""
        for number in state_list:
            state_number += str(number)
        
        state_number = int(state_number)

        return state_number

    def _number_to_list(self, state_number):
        state_number = str(state_number)
        while len(state_number) != 9:
            state_number = "0" + state_number

        state_list = []
        for char in state_number:
            state_list.append(int(char))

        return state_list

def check_winner(state):
    for i in range(3):
        #Checks win by column:
        if state[i] == state[3 + i] and state[i] == state[6 + i]:
            #Avoids returning when there are still winning possibilities
            if state[i] != 0:
                return state[i]

        #Checks win by row:
        if state[3 * i] == state[3 * i + 1] and state[3 * i] == state[3 * i + 2]:
            if state[3 * i] != 0:
                return state[3 * i]

        #Checks win by cross:
        if i != 2:
            if state[2 * i] == state[4] and state[4] == state[8 - 2 * i]:
                if state[2 * i] != 0:
                    return state[2 * i]
        
        #Checks for draws by filled states, draw == -1
        for number in state:
            if number == 0:
                return 0

    return 3

player1 = Player(1,0.1,0.1)
player2 = Player(2,0.1,0.1)
game = Game(player1, player2)

game.train(10000)
print(game.player1.values[a])