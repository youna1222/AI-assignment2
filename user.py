from util import *

class User:
    def __init__(self, y=0, x=0, move='v1'):
        self.y = y
        self.x = x
        self.move = move

        self.q = {}
        self.prob_random_action = 0.05
        self.discount = 0.8
        self.lr = 0.003

        self.weights = {'bias': 0.0, 'next-ghost': 0.0, 'next-eat': 0.0, 'closest-item': 0.0, 'next-power': 0.0, 'next-power-close-ghost': 0.0, 'too-many-next-ghost': 0.0, 'next-next-eat': 0.0, 'trap-while-ghost': 0.0, 'blank': 0.0, 'recent-visit': 0.0}

        self.recent_visit = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]

    def next_pos(self, state, test=False):
        if self.move == 'v1':
            return self.next_pos_v1(state)
        if self.move == 'v2':
            return self.next_pos_v2(state, test)
        if self.move == 'v3':
            return self.next_pos_v3(state, test)

    def next_pos_v1(self, state):
        cand_pos = []
        if state[self.y - 1][self.x] != WALL:
            cand_pos.append((self.y - 1, self.x))
        if state[self.y][self.x - 1] != WALL:
            cand_pos.append((self.y, self.x - 1))
        if state[self.y][self.x + 1] != WALL:
            cand_pos.append((self.y, self.x + 1))
        if state[self.y + 1][self.x] != WALL:
            cand_pos.append((self.y + 1, self.x))
        return random.choice(cand_pos)

    def get_legal_actions(self, state):
        y, x = self.y, self.x
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] in [USER, PUSER]:
                    y, x = i, j
        actions = []
        if state[y - 1][x] != WALL:
            actions.append(0)
        if state[y][x - 1] != WALL:
            actions.append(1)
        if state[y][x + 1] != WALL:
            actions.append(2)
        if state[y + 1][x] != WALL:
            actions.append(3)
        return actions

    def possible_actions_count(self, state, y, x):
        count = 0
        if state[y - 1][x] != WALL:
            count += 1
        if state[y][x - 1] != WALL:
            count += 1
        if state[y][x + 1] != WALL:
            count += 1
        if state[y + 1][x] != WALL:
            count += 1
        return count

    def hash_state(self, state):
        return hashlib.md5(repr(state).encode('utf-8')).hexdigest()

    def get_q(self, state, action):
        state = self.hash_state(state)
        if (state, action) not in self.q:
            return 0.0
        return self.q[(state, action)]

    def get_v(self, state):
        actions = self.get_legal_actions(state)
        if len(actions) == 0:
            return 0.0
        max_action = max(actions, key=lambda a: self.get_q(state, a))
        return self.get_q(state, max_action)

    def get_action_from_q(self, state):
        actions = self.get_legal_actions(state)
        if len(actions) == 0:
            return None
        max_action = max(actions, key=lambda a: self.get_q(state, a))
        q_val = self.get_q(state, max_action)
        max_actions = [a for a in actions if self.get_q(state, a) == q_val]
        return random.choice(max_actions)

    def get_action(self, state):
        actions = self.get_legal_actions(state)
        if len(actions) == 0:
            return None
        if random.random() < self.prob_random_action:
            return random.choice(actions)
        return self.get_action_from_q(state)

    def update(self, state, action, next_state, reward):
        if self.move == 'v2':
            return self.update_v2(state, action, next_state, reward)
        elif self.move == 'v3':
            return self.update_v3(state, action, next_state, reward)

    def update_v2(self, state, action, next_state, reward):
        state = self.hash_state(state)
        q_val = self.get_q(state, action)
        sample = reward + self.discount * self.get_v(next_state)
        self.q[(state, action)] = (1 - self.lr) * q_val + self.lr * sample

    def next_pos_v2(self, state, test=False):
        if test:
            action = self.get_action_from_q(state)
        else:
            action = self.get_action(state)
        if action == 0:
            next_pos = (self.y - 1, self.x)
        elif action == 1:
            next_pos = (self.y, self.x - 1)
        elif action == 2:
            next_pos = (self.y, self.x + 1)
        else:
            next_pos = (self.y + 1, self.x)
        return next_pos

    def get_closest_item(self, state, y, x):
        if state[y][x] not in [BLANK, ITEM, POWER]:
            return 0.0
        q = deque([(y, x, 1)])
        visit = set()
        while len(q) > 0:
            y, x, size = q.popleft()
            if state[y][x] in [ITEM, POWER]:
                return size
            if (y, x) in visit:
                continue
            visit.add((y, x))
            if state[y - 1][x] in [BLANK, ITEM, POWER]:
                q.append((y - 1, x, size + 1))
            elif state[y][x - 1] in [BLANK, ITEM, POWER]:
                q.append((y, x - 1, size + 1))
            elif state[y][x + 1] in [BLANK, ITEM, POWER]:
                q.append((y, x + 1, size + 1))
            elif state[y + 1][x] in [BLANK, ITEM, POWER]:
                q.append((y + 1, x, size + 1))
        return 0.0



    def calculate_feature(self, state, next_y, next_x, feature, type):
        if state[next_y][next_x] == type:
            feature += 1.0
        if next_y > 0 and state[next_y - 1][next_x] == type:
            feature += 1.0
        if next_x > 0 and state[next_y][next_x - 1] == type:
            feature += 1.0
        if next_x < len(state[0]) - 1 and state[next_y][next_x + 1] == type:
            feature += 1.0
        if next_y < len(state) - 1 and state[next_y + 1][next_x] == type:
            feature += 1.0
        return feature

    def get_features(self, state, action):
        y, x = self.y, self.x
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] in [USER, PUSER]:
                    y, x = i, j
        if action == 0:
            next_y, next_x = y - 1, x
        elif action == 1:
            next_y, next_x = y, x - 1
        elif action == 2:
            next_y, next_x = y, x + 1
        else:
            next_y, next_x = y + 1, x

        features = {'bias': 1.0}
        features['next-ghost'] = 0.0
        features['next-power-close-ghost'] = 0.0
        features['trap-while-ghost'] = 0.0

        count = 0
        if state[next_y - 1][next_x] != WALL and state[next_y - 1][next_x] != GHOST:
            count += 1
        if state[next_y][next_x - 1] != WALL and state[next_y - 1][next_x] != GHOST:
            count += 1
        if state[next_y][next_x + 1] != WALL and state[next_y - 1][next_x] != GHOST:
            count += 1
        if state[next_y + 1][next_x] != WALL and state[next_y - 1][next_x] != GHOST:
            count += 1

        features['next-ghost'] = self.calculate_feature(state, next_y, next_x, features['next-ghost'], GHOST)
        features['too-many-next-ghost'] = 0.0
        if features['next-ghost'] > 1:
            features['too-many-next-ghost'] += 1.0
        if features['next-ghost'] >= 1:
            if state[next_y][next_x] == POWER:
                features['next-power-close-ghost'] += 1.0
            #self.calculate_feature(state, next_y, next_x, features['next-power-close-ghost'], POWER)
            if count < 2:
                features['trap-while-ghost'] += 1.0

        features['next-eat'] = 0.0
        if state[next_y][next_x] == ITEM:
            features['next-eat'] += 1.0
        #self.calculate_feature(state, next_y, next_x, features['next-eat'], ITEM)

        features['blank'] = 0.0
        if state[next_y][next_x] == BLANK:
            features['blank'] += 1.0
        #self.calculate_feature(state, next_y, next_x, features['blank'], BLANK)

        features['next-power'] = 0.0
        if state[next_y][next_x] == POWER:
            features['next-power'] += 1.0
        #self.calculate_feature(state, next_y, next_x, features['next-power'], POWER)
        features['closest-item'] = self.get_closest_item(state, next_y, next_x)

        features['recent-visit'] = 0.0
        for r in self.recent_visit:
            if r == (next_y, next_x):
                features['recent-visit'] += 1.0

        #features['visited'] = 0.0
        #if self.visited[next_y][next_x] == True:
        #    features['visited'] += 1.0
        #self.calculate_feature(self.visited, next_y, next_x, features['visited'], True)

        return features



    def get_q_v3(self, state, action):
        ret = 0.0
        features = self.get_features(state, action)
        for key in features:
            ret += features[key] * self.weights[key]
        return ret

    def get_v_v3(self, state):
        actions = self.get_legal_actions(state)
        if len(actions) == 0:
            return 0.0
        max_action = max(actions, key=lambda a: self.get_q_v3(state, a))
        return self.get_q_v3(state, max_action)

    def get_action_from_q_v3(self, state):
        actions = self.get_legal_actions(state)
        if len(actions) == 0:
            return None
        max_action = max(actions, key=lambda a: self.get_q_v3(state, a))
        q_val = self.get_q_v3(state, max_action)
        max_actions = [a for a in actions if self.get_q_v3(state, a) == q_val]
        return random.choice(max_actions)

    def get_action_v3(self, state):
        actions = self.get_legal_actions(state)
        if len(actions) == 0:
            return None
        if random.random() < self.prob_random_action:
            return random.choice(actions)
        return self.get_action_from_q_v3(state)

    def update_v3(self, state, action, next_state, reward):
        delta = reward + self.discount * self.get_v_v3(next_state) - self.get_q_v3(state, action)
        features = self.get_features(state, action)
        weights = copy.deepcopy(self.weights)
        for key in features:
            features[key] = features[key] * self.lr * delta
            weights[key] += features[key]
        self.weights = copy.deepcopy(weights)

    def next_pos_v3(self, state, test=False):
        if test:
            action = self.get_action_from_q_v3(state)
        else:
            action = self.get_action_v3(state)
        if action == 0:
            next_pos = (self.y - 1, self.x)
        elif action == 1:
            next_pos = (self.y, self.x - 1)
        elif action == 2:
            next_pos = (self.y, self.x + 1)
        else:
            next_pos = (self.y + 1, self.x)
        self.recent_visit.pop()
        self.recent_visit.append(next_pos)
        #print(self.visited)
        return next_pos
