walls="x xx  xx x"
sensors=["on","on","off","on"]
# your code starts

NODE_LIST = []
NUM_OF_WALLS = walls.count("x")
TOPOLOGY_SIZE = walls.__len__()
NUM_OF_STEPS = len(sensors)
PREV_PROBABILITIES = [1.1]*walls.__len__()


#my solution is essentially utilizes markov's chain. I drew a state diagram and calulated two transition matrices to multiply with state vector.
#I have two matrices for state transitions. Depending on the input sequence, I apply the two on the state vector.

#for the algorithm, taken help from: https://towardsdatascience.com/markov-and-hidden-markov-model-3eec42298d75



class L:

    def __init__(self, curr_prob, s_on_prob, s_off_prob, trans_prob, refl_prob):
        self.current_probability = curr_prob
        self.sensor_on_probability = s_on_prob
        self.sensor_off_probability = s_off_prob
        self.transition_probability = trans_prob
        self.reflection_probability = refl_prob


def __normalize_probabilities__():
    probability_sums = 0.
    for node in NODE_LIST:
        probability_sums += node.current_probability

    for node in NODE_LIST:
        node.current_probability /= probability_sums


def state_transition(sensor_input):

    PREV_PROBABILITIES =  list(map(lambda x: x.current_probability , NODE_LIST))

    if sensor_input == "on":
        NODE_LIST[0].current_probability *= NODE_LIST[0].sensor_on_probability * NODE_LIST[0].reflection_probability
        for i in range(1, TOPOLOGY_SIZE): #the matrix multiplication for markov chain of on state transition
            div = NODE_LIST[i].reflection_probability + NODE_LIST[i].transition_probability
            NODE_LIST[i].current_probability = (PREV_PROBABILITIES[i] * NODE_LIST[i].sensor_on_probability * NODE_LIST[i].reflection_probability + PREV_PROBABILITIES[i-1] * NODE_LIST[i-1].transition_probability * NODE_LIST[i-1].sensor_on_probability) / div

    else:
        NODE_LIST[0].current_probability *= NODE_LIST[0].sensor_off_probability * NODE_LIST[0].reflection_probability
        for i in range(1, TOPOLOGY_SIZE - 1): #the matrix multiplicaiton for markov chain of off state transition 
            div = NODE_LIST[i].reflection_probability + NODE_LIST[i].transition_probability
            NODE_LIST[i].current_probability = (PREV_PROBABILITIES[i] * NODE_LIST[i].sensor_off_probability * NODE_LIST[i].reflection_probability + PREV_PROBABILITIES[i-1] * NODE_LIST[i-1].transition_probability * NODE_LIST[i-1].sensor_off_probability) /div


def __node_list_initialization__():
    for i in range(0, TOPOLOGY_SIZE):
        current_probability = 1. / TOPOLOGY_SIZE
        s_on_prob = 0.7 if walls[i] == "x" else 0.2
        s_off_prob = 1. - s_on_prob
        trans_prob = 0.6 if (((i+1) % 2) == 1) else 0.8
        refl_prob = 0.4 if (((i+1) % 2) == 1) else 0.2
        if i == TOPOLOGY_SIZE - 1:
            trans_prob = 0.
            refl_prob = 1.
        NODE_LIST.append(L(current_probability, s_on_prob, s_off_prob, trans_prob, refl_prob))

def main():
    __node_list_initialization__()

    for i in range(0, NUM_OF_STEPS):
        state_transition(sensors[i])
        
    __normalize_probabilities__()

    robot_pos = 1
    robot_pos_prob = NODE_LIST[0].current_probability
    for i in range(1, TOPOLOGY_SIZE):
        if NODE_LIST[i].current_probability > robot_pos_prob:
            robot_pos_prob = NODE_LIST[i].current_probability
            robot_pos = i + 1

    for node in NODE_LIST:
        print("hello: ", node.current_probability)
    
# your code ends
    print('The most likely current position of the robot is',robot_pos,'with probability',robot_pos_prob)


if __name__ == '__main__':
    main()    