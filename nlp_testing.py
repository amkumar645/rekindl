import numpy as np
import pickle

def sigmoid(z):
  return 1 / (1 + np.exp(-z))

def cross_entropy_loss(X, y, w):
  u = X.T@w
  cross_entropies = -(y*np.log(sigmoid(u)) + (1-y)*np.log(1-sigmoid(u)))
  return np.mean(cross_entropies)

def grad_CEloss(X, y, w):
  grads = (sigmoid(X.T@w) - y) * X
  return np.mean(grads, axis=1)


nlp = pickle.load(open('./nlp_md.pkl', 'rb'))
# testing for threshold value
# words we want the model to report as similar
file = open('similar_words.txt', 'r')
similar_sims = []
line = file.readline()
while line != '':
    words = line.split(', ')
    first_word = nlp(words[0])
    sims = [first_word.similarity(nlp(x)) for x in words[1:]]
    for num in sims:
        similar_sims.append(num)
    line = file.readline()
similar_sims = np.array(similar_sims)
file.close()

# words we want the model to report as similar
file = open('dissimilar_words.txt', 'r')
dissimilar_sims = []
line = file.readline()
while line != '':
    words = line.split(', ')
    dissimilar_sims.append(nlp(words[0]).similarity(nlp(words[1])))
    line = file.readline()
dissimilar_sims = np.array(dissimilar_sims)
file.close()

# logisitic regression with gradient descent to find weight vector to classify
# similarity (w[0]*similarity + w[1] >= 0 means similar, o/w dissimilar)
ns = len(similar_sims)
nd = len(dissimilar_sims)
X0 = np.hstack((np.expand_dims(similar_sims,axis=1), np.ones((ns,1))))
X1 = np.hstack((np.expand_dims(dissimilar_sims,axis=1), np.ones((nd,1))))
X = np.vstack((X0, X1)).T
y = np.hstack((np.ones(ns), np.zeros(nd)))

eps = 10**(-3)
gamma = 0.1
w_init = [1, -0.5]
w_vals = [w_init]
i = 0
while True:
  grad = grad_CEloss(X, y, w_vals[i])
  if np.linalg.norm(grad) < eps:
    break
  w_vals.append(list(w_vals[i] - gamma*grad))
  i += 1
w_vals = np.array(w_vals)

w = w_vals[i]
print(w)

def top_two_common_interests(common_interests, common_similarities):
    num_common = len(common_interests)
    top_two = []
    if num_common > 0:
        max_index = np.argmax(common_similarities)
        top_two.append(common_interests[max_index])
        common_similarities[max_index] = -1
        if num_common > 1:
            next_max_index = np.argmax(common_similarities)
            top_two.append(common_interests[next_max_index])
    return top_two

def interest_similarity(p1, p2):
    m = len(p1)
    n = len(p2)
    common_interests = []
    common_similarities = []
    for i in range(m):
        for j in range(n):
            similarity = nlp(p1[i]).similarity(nlp(p2[j]))
            if w[0] * similarity + w[1] >= 0:
                common_interests.append((p1[i], p2[j]))
                common_similarities.append(similarity)
    
    return top_two_common_interests(common_interests, common_similarities)


# testing
num_people = 4
interests = []
for i in range(num_people):
    f = open(f"person{i}.txt", 'r')
    interests.append(f.readline().split(", "))
    print(f"p{i} interests: {interests[i]}")

for i in range(num_people):
    for j in range(num_people):
        if j > i:
            common_interests = interest_similarity(interests[i], interests[j])
            print(f"Common interests between p{i} and p{j}:\n{common_interests}")

