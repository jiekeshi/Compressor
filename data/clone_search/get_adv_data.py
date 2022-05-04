import csv
import json
import random

csv.field_size_limit(100000000)

# adv_data = []
# for index in range(2):
#     with open("../../../code/attack_greedy_train_subs_"+str(index*300)+"_"+str((index+1)*300)+".csv") as rf:
#         reader = csv.DictReader(rf)
#         for row in reader:
#             if row["Is Success"] == "1":
#                 adv_data.append(row["Adversarial Code"].replace("\n", "\\n") + " <CODESPLIT> " + row["True Label"] + '\n')
# print(len(adv_data))
# with open("./dataset/train.jsonl") as rf:
#     for line in rf:
#         adv_data.append(json.loads(line.strip()))
# print(len(adv_data))
# random.shuffle(adv_data)

# with open("./adv_train.txt", "w") as wf:
#     for item in adv_data:
#         wf.write(item)

adv_data_test = []
for index in range(8):
    with open("attack_GA_"+str(index*500)+"_"+str((index+1)*500)+".csv") as rf:
        reader = csv.DictReader(rf)
        for row in reader:
            if row["Is Success"] == "1":
                adv_data_test.append({"target":int(row["True Label"]), "func":row["Adversarial Code"], "idx":None})
print(len(adv_data_test))
random.shuffle(adv_data_test)

with open("adv_test.jsonl", "w") as wf:
    for item in adv_data_test:
        wf.write(json.dumps(item)+'\n')


# adv_data_test_greedy = []
# for index in range(7):
#     with open("../code/attack_genetic_test_subs_"+str(index*400)+"_"+str((index+1)*400)+".csv") as rf:
#         reader = csv.DictReader(rf)
#         for row in reader:
#             if row["Is Success"] == "1" and row["Attack Type"] == "Greedy":
#                 adv_data_test_greedy.append({"target":int(row["True Label"]), "func":row["Adversarial Code"], "idx":None})
# print(len(adv_data_test_greedy))

# random.shuffle(adv_data_test_greedy)

# with open("./adv_test_greedy.jsonl", "w") as wf:
#     for item in adv_data_test_greedy:
#         wf.write(json.dumps(item)+'\n')

# adv_data_test_mhm = []
# for index in range(7):
#     with open("../code/mhm_attack_lstest_subs_"+str(index*400)+"_"+str((index+1)*400)+".csv") as rf:
#         reader = csv.DictReader(rf)
#         for row in reader:
#            if row["Is Success"] == "1":
#                 adv_data_test_mhm.append({"target":int(row["True Label"]), "func":row["Adversarial Code"], "idx":None})
# print(len(adv_data_test_mhm))

# random.shuffle(adv_data_test_mhm)

# with open("./adv_test_mhm.jsonl", "w") as wf:
#     for item in adv_data_test_mhm:
#         wf.write(json.dumps(item)+'\n')